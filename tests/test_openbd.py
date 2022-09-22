from openbd import book_info


def test_book_info():
    bi = book_info("4764905809")
    assert bi.isbn == "9784764905801"
