import fpdf
from database.database import get_id_last_invoices

fpdf.SYSTEM_TTFONTS = 'C:/Windows/Fonts'


# Создание PDF накладной.
async def create_pdf_invoice(tg_id: int, characteristics: list[str]):
    pdf = fpdf.FPDF()
    pdf.add_page()
    pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
    pdf.set_font('DejaVu', size=15)
    title_points = ('Описание груза: ', 'Вес груза: ', 'Габариты груза: ',
                    'Адрес отправки: ', 'Адрес получения: ', 'Способ оплаты: ')
    number_invoice = await get_id_last_invoices()
    pdf.cell(200, 10, txt='Номер накладной: ' + str(number_invoice), ln=1, align='L')
    for i in range(len(title_points)):
        txt = title_points[i] + characteristics[i]
        pdf.cell(200, 10, txt=txt, ln=1, align='L')

    name_file = str(tg_id) + ' invoice.pdf'
    pdf.output(name_file)
