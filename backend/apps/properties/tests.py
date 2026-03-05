# apps/properties/tests.py
import pytest

LIST_URL   = "/api/v1/properties/"
CREATE_URL = "/api/v1/properties/create/"
MINE_URL   = "/api/v1/properties/mine/"


@pytest.mark.django_db
class TestPropertyList:
    def test_active_visible_public(self, api_client, property_obj):
        r = api_client.get(LIST_URL)
        assert r.status_code == 200
        assert str(property_obj.id) in [x["id"] for x in r.data["results"]]

    def test_draft_hidden(self, api_client, property_obj):
        property_obj.status = "DRAFT"
        property_obj.save()
        r = api_client.get(LIST_URL)
        assert str(property_obj.id) not in [x["id"] for x in r.data["results"]]

    def test_filter_county(self, api_client, property_obj):
        r = api_client.get(LIST_URL + "?county=Nairobi")
        assert r.status_code == 200

    def test_filter_max_price_excludes(self, api_client, property_obj):
        r = api_client.get(LIST_URL + "?max_price=1000000")
        assert str(property_obj.id) not in [x["id"] for x in r.data["results"]]

    def test_filter_min_price_includes(self, api_client, property_obj):
        r = api_client.get(LIST_URL + "?min_price=1000000")
        assert str(property_obj.id) in [x["id"] for x in r.data["results"]]

    def test_filter_property_type(self, api_client, property_obj):
        r = api_client.get(LIST_URL + "?property_type=RESIDENTIAL")
        assert str(property_obj.id) in [x["id"] for x in r.data["results"]]

    def test_search(self, api_client, property_obj):
        r = api_client.get(LIST_URL + "?search=Westlands")
        assert r.status_code == 200

    def test_ordering_by_price(self, api_client, property_obj):
        r = api_client.get(LIST_URL + "?ordering=price_kes")
        assert r.status_code == 200


@pytest.mark.django_db
class TestPropertyCreate:
    def test_seller_can_create(self, seller_client):
        r = seller_client.post(CREATE_URL, {
            "title": "New Plot Karen", "description": "Beautiful plot",
            "county": "Nairobi", "area_name": "Karen",
            "lr_number": "LR/999/001", "property_type": "RESIDENTIAL",
            "size_acres": "0.25", "price_kes": 8_000_000,
        })
        assert r.status_code == 201

    def test_buyer_blocked(self, buyer_client):
        r = buyer_client.post(CREATE_URL, {
            "title": "Plot", "description": "desc", "county": "Nairobi",
            "area_name": "x", "lr_number": "LR/1/1",
            "property_type": "RESIDENTIAL", "size_acres": "0.25", "price_kes": 8_000_000,
        })
        assert r.status_code == 403

    def test_unauthenticated_blocked(self, api_client):
        r = api_client.post(CREATE_URL, {})
        assert r.status_code == 401

    def test_invalid_lr_number(self, seller_client):
        r = seller_client.post(CREATE_URL, {
            "title": "Plot", "description": "desc", "county": "Nairobi",
            "area_name": "x", "lr_number": "!!INVALID!!",
            "property_type": "RESIDENTIAL", "size_acres": "0.25", "price_kes": 8_000_000,
        })
        assert r.status_code == 400

    def test_price_too_low(self, seller_client):
        r = seller_client.post(CREATE_URL, {
            "title": "Plot", "description": "desc", "county": "Nairobi",
            "area_name": "x", "lr_number": "LR/1/2",
            "property_type": "RESIDENTIAL", "size_acres": "0.25", "price_kes": 500,
        })
        assert r.status_code == 400

    def test_size_zero_rejected(self, seller_client):
        r = seller_client.post(CREATE_URL, {
            "title": "Plot", "description": "desc", "county": "Nairobi",
            "area_name": "x", "lr_number": "LR/1/3",
            "property_type": "RESIDENTIAL", "size_acres": "0", "price_kes": 500_000,
        })
        assert r.status_code == 400


@pytest.mark.django_db
class TestPropertyDetail:
    def test_get_active(self, api_client, property_obj):
        r = api_client.get(f"{LIST_URL}{property_obj.id}/")
        assert r.status_code == 200
        assert r.data["id"] == str(property_obj.id)
        assert "lr_number_encrypted" not in r.data
        assert "seller_name" in r.data

    def test_draft_returns_404(self, api_client, property_obj):
        property_obj.status = "DRAFT"
        property_obj.save()
        r = api_client.get(f"{LIST_URL}{property_obj.id}/")
        assert r.status_code == 404


@pytest.mark.django_db
class TestMyListings:
    def test_seller_sees_own(self, seller_client, property_obj):
        r = seller_client.get(MINE_URL)
        assert r.status_code == 200
        assert str(property_obj.id) in [x["id"] for x in r.data["results"]]

    def test_buyer_sees_nothing(self, buyer_client, property_obj):
        r = buyer_client.get(MINE_URL)
        assert r.status_code == 200
        assert len(r.data["results"]) == 0