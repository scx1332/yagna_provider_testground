from collections import Iterable

from rich.console import Console
from rich.table import Table
from yapapi.rest import payment, market
import json


def print_invoice(console: Console, invoices: "Iterable[payment.Invoice]"):
    table = Table("id", "issuer", "amount", "status")
    for invoice in invoices:
        table.add_row(invoice.invoice_id, invoice.issuer_id, invoice.amount, str(invoice.status))

    console.print(table)


def print_offer(
    console: Console,
    event: market.OfferProposal,
    det: market.AgreementDetails,
):
    table = Table("provider", "requestor", title=f"offer {event.id}")
    table.add_row(
        json.dumps(det.provider_view.properties, indent=4),
        json.dumps(det.requestor_view.properties, indent=4),
    )
    console.print(table)


__all__ = ["print_invoice", "print_offer"]
