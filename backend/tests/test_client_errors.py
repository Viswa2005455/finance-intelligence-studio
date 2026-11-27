import logging


def test_report_is_logged_on_one_line(anon_client, caplog):
    with caplog.at_level(logging.ERROR, logger="fis.client"):
        r = anon_client.post("/api/client-errors", json={"message": "Boom\nFAKE LOG LINE", "page": "/dcf?token=secret#x", "stack": "at a\nat b", "version": "0.14.0"})
    assert r.status_code == 202
    line = caplog.records[-1].getMessage()
    assert "\n" not in line and "/dcf" in line and "secret" not in line and "0.14.0" in line


def test_limited_per_address(anon_client):
    codes = [anon_client.post("/api/client-errors", json={"message": f"e{i}"}).status_code for i in range(12)]
    assert codes[:10] == [202] * 10 and codes[10] == 429


def test_rejects_empty(anon_client):
    assert anon_client.post("/api/client-errors", json={"message": ""}).status_code == 422
