import adsk.core


def file_select(title, filter):
    app = adsk.core.Application.get()
    ui = app.userInterface
    # Set styles of file dialog.
    fileDlg = ui.createFileDialog()
    fileDlg.isMultiSelectEnabled = False
    fileDlg.title = title
    fileDlg.filter = filter

    # Show file open dialog
    dlgResult = fileDlg.showOpen()
    if dlgResult == adsk.core.DialogResults.DialogOK:
        return fileDlg.filename
    else:
        raise FileNotFoundError
