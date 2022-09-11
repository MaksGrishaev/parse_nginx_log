import re
import csv
import git
import sys
import getopt
from pathlib import Path
from datetime import datetime


def load_log(path):
    parsed_log = []
    with open(path, mode="r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            parsed_log.append(parse(line))
    return parsed_log


def parse(line):
    reg_exp = re.compile(r'(?P<ip>.*?)- - \[(?P<time>.*?)\] "(?P<request>.*?)" (?P<status>.*?) '
                         r'(?P<bytes>.*?) "(?P<referer>.*?)" "(?P<client_info>.*?)"')
    return reg_exp.match(line).groups()


def write_csv(parsed_log, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for line in parsed_log:
            writer.writerow(line)


def git_flow(path_to_log="nginx.log", path_to_result=None, repo=None):
    result_file = "parsed/nginx.csv" if not path_to_result else path_to_result
    path = Path(result_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    result_dir = str(path.absolute().parent)

    if repo:
        if repo.startswith("https://") or repo.startswith("git@"):
            try:
                git.Repo.clone_from(repo, result_dir)
            except git.exc.GitCommandError as error:
                print(f'Error creating remote: {error}')

    write_csv(load_log(path_to_log), path.absolute())

    try:
        git_repo = git.Repo.init(result_dir)

        git_repo.index.add(str(path.absolute()))
        git_repo.index.commit(f"Log is updated {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

        if repo:
            if repo.startswith("git@"):
                print("Sorry! I don't work via ssh yet...")
                sys.exit()
            if repo.startswith("https://"):
                try:
                    for remote in git_repo.remotes:
                        if remote.name == 'origin':
                            git_repo.delete_remote('origin')
                    remote = git_repo.create_remote('origin', url=repo)
                    git_repo.remotes.origin.push('master')
                except git.exc.GitCommandError as error:
                    print(f'Error creating remote: {error}')

    except git.exc.InvalidGitRepositoryError:
        print(f"You should specify directory with existing repository "
              f"or execute command 'git init' inside directory {result_dir} to create a new git repository")


def main(argv):
    """
    parse_nginx_log.py -i <input_file> -o <output_file> -g <git_repository>
    -i - input file - nginx log file
    -o - output file - result file with parsed data
    -g - git repository
    :return:
    none
    """
    ifile = None
    ofile = None
    repo = None
    try:
        opts, args = getopt.getopt(argv, "hi:o:g:", ["ifile=", "ofile=", "git="])
    except getopt.GetoptError:
        print("parse_nginx_log.py -i <input_file> -o <output_file> -g <git_repository>")
        sys.exit()

    for opt, arg in opts:
        if opt == '-h':
            print("parse_nginx_log.py -i <input_file> -o <output_file> -g <git_repository>")
            sys.exit()
        elif opt in ("-i", "--ifile"):
            ifile = arg
        elif opt in ("-o", "--ofile"):
            ofile = arg
        elif opt in ("-g", "--git", "--repo"):
            repo = arg
            print(repo)
        else:
            print("parse_nginx_log.py -i <input_file> -o <output_file> -g <git_repository>")
            sys.exit()

    if not ifile:
        ifile = "nginx.log"

    git_flow(ifile,ofile, repo)


if __name__ == '__main__':
    #write_csv(load_log("nginx.log"))
    # main(repo="https://github.com/MaksGrishaev/test_logs.git")
    # git_flow(repo="https://github.com/MaksGrishaev/test_logs1.git")
    main(sys.argv[1:])
