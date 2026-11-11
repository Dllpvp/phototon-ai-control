from app.security.masking import detokenize, mask


def test_roundtrip_for_string_value_inside_dict() -> None:
    original = {"note": "Анна Петрова связалась с Клиент №7 на сумму 1 200 BYN"}
    masked, vault = mask(original)
    assert detokenize(masked["note"], vault) == original["note"]


def test_vault_originals_are_not_in_masked_context() -> None:
    masked, vault = mask({"note": "Анна Петрова: B2B Фотостудия Луч, счет 120 BYN"})
    serialized = repr(masked)
    assert vault, "vault не должен быть пустым"
    for original in vault.values():
        assert original not in serialized
    # сам vault (mapping token -> original) не встроен в masked-контекст
    assert "vault" not in masked


def test_strict_masks_money_and_standard_preserves_it() -> None:
    context = {"note": "Оплачено 120 BYN", "amount_byn": "250 BYN"}
    strict, _ = mask(context, level="strict")
    standard, _ = mask(context, level="standard")
    assert "[AMT_" in strict["note"]
    assert "[AMT_" in strict["amount_byn"]
    assert "120 BYN" in standard["note"]
    assert standard["amount_byn"] == "250 BYN"


def test_same_entity_gets_same_token_within_call() -> None:
    masked, _ = mask({"first": "Анна Петрова", "second": "Анна Петрова"})
    assert masked["first"] == masked["second"]


def test_standard_masks_people_and_clients_but_not_amounts() -> None:
    original = {"note": "Анна Петрова, B2B Фотоцентр, 75 BYN"}
    masked, _ = mask(original, level="standard")
    assert "[EMP_01]" in masked["note"]
    assert "[CLIENT_01]" in masked["note"]
    assert "75 BYN" in masked["note"]
