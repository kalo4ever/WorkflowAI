from api.services.event_handler import _EventRouter, _jobs  # pyright: ignore [reportPrivateUsage]


# TODO: this test is useless, instead once all events are in the same file, we should make
# sure that all events are represented
def test_event_exhaustive():
    router = _EventRouter()
    keys = set(router._handlers.keys())  # pyright: ignore [reportPrivateUsage]

    assert {job.event for job in _jobs()} == keys
