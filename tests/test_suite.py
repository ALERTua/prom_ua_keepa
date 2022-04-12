from prom_ua_keepa import common_tools as tools
from global_logger import Log

LOG = Log.get_logger()


def test_liters():
    liters_input = [
        'asd 0.7L asd',
        'asd 0.7 L asd',
        'asd 0,7L asd',
        'asd 0,7 L asd',

        'asd 0.7л asd',
        'asd 0,7л asd',
        'Виски Ardbeg 10 y.o. в коробке 0.7 л',
        'asd 0,7 Л asd',

        'asd 1L asd',
        'asd 1Л asd',
        'asd 1 L asd',
        'asd 1 Л asd',

        'asd 1.0L asd',
        'asd 1,0L asd',
        'asd 1.0 L asd',
        'asd 1,0 L asd',

        'asd 1.0Л asd',
        'asd 1,0Л asd',
        'asd 1.0 Л asd',
        'asd 1,0 Л asd',
    ]
    liters_output = []
    for i in liters_input:
        liters_output.append(tools.liters(i))
    liters_output = [i for i in liters_output if i]
    assert len(liters_input) == len(liters_output)


if __name__ == '__main__':
    LOG.verbose = True
    test_liters()
    print("")
