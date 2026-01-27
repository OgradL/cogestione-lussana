
import os
import openpyxl

from cogestione import db as database


def carica_utenti(path):

    if not os.path.exists(path):
        print("path does not exists")
        return

    wb = openpyxl.load_workbook(path)
    ws = wb.active

    if ws is None:
        return

    db = database.get_db()
    for value in ws.iter_rows(min_row=2):
        db.session.add(database.user(
            email = str(value[6].value),
            nome = str(value[1].value) if value[1].value is not None else "",
            cognome = str(value[0].value),
            classe = str(value[5].value),
            password = ""
        ))
        db.session.commit()



def carica_prof(path):

    if not os.path.exists(path):
        print("path does not exists")
        return

    wb = openpyxl.load_workbook(path)
    ws = wb.active

    if ws is None:
        return

    db = database.get_db()
    for value in ws.iter_rows(min_row=2):
        db.session.add(database.user(
            email = str(value[1].value),
            nome = "",
            cognome = str(value[0].value),
            classe = "docente",
            password = ""
        ))
        db.session.commit()

