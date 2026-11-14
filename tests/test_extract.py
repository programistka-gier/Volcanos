from unittest.mock import patch

from extract.extract import extract_volcanoes_from_noaa

# TODO: napisz pierwszy test.
#
# Cel: sprawdzić, że extract_volcanoes_from_noaa() poprawnie łączy dane
# z wielu stron paginacji w jedną listę, bez uderzania w prawdziwe NOAA API.
#
# Podpowiedzi (nie gotowiec):
# - użyj @patch("extract.extract.requests.get") jako dekoratora nad funkcją testową
#   (patchujemy requests.get w MIEJSCU, gdzie jest używany — czyli w module extract.extract,
#   nie tam gdzie jest zdefiniowany w bibliotece requests)
# - mock_get.side_effect = [...] pozwala zwrócić różne odpowiedzi na kolejne wywołania
#   (pierwsze wywołanie sprawdza totalPages, kolejne pobierają strony)
# - każdy element side_effect to obiekt, który musi mieć .json() i .raise_for_status()
#   (Mock(**{"json.return_value": {...}}) albo osobna klasa pomocnicza)
# - assert na końcu: czy zwrócona lista ma oczekiwaną długość / zawartość


def test_extract_volcanoes_from_noaa_success():
    pass
