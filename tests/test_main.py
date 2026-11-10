from semestralni_prace.main import main


def test_main_prints_title(capsys):
    main()
    assert "Semestralni prace" in capsys.readouterr().out
