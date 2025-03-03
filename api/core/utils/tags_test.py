from .tags import compute_tags


def test_compute_tags() -> None:
    data = {
        "key1": "value1",
        "key2": 2.0,  # float should print 2
        "key21": 2.00,  # float should print 2
        "key3": {"key4": "value4"},
        "key5": "A REALY LONG VALUE FERZOIJFZOIJFEOIJFEOIZFJEOIIZJFIZOJFEIOZ",  # cut
        "key6": "",  # skipped
        "key7": None,  # skipped,
        "key8": 0,  # included
        "key9": 0.0,  # included
        "key10": 1.1805485498549,  # float should print 1.18
    }
    assert compute_tags(data, 10) == [
        "key1=value1",
        "key10=1.18",
        "key2=2",
        "key21=2",
        'key3={"key4": "',
        "key5=A REALY LO",
        "key8=0",
        "key9=0",
    ]
