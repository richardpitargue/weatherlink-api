import sys

from updater import Updater
import time

def main(argv):
    updater = Updater('sarai-aws.txt')
    updater.update_all()

    # while True:
    #     updater.update_all()
    #     print('\nSleeping for 15 minutes...\n')
    #     time.sleep(900)


if __name__ == '__main__':
    main(sys.argv[1:])
