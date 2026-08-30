"""Original D-104 payment-domain UML class fixture for P-19B review-24."""
from semantic_fixtures import e, finalize, member, n


def _attribute(item_id, name, data_type):
    return member(item_id, "attribute", name, data_type=data_type, visibility="private")


def _operation(item_id, name, signature):
    return member(item_id, "operation", name, signature=signature, visibility="public")


def uml_class_fixture():
    containers = [
        n("class-billing-service", "class", "BillingService", members=[
            _operation("operation-billing-charge", "charge", "charge(invoice: Invoice): Receipt"),
        ]),
        n("interface-payment-option", "class", "PaymentOption", members=[
            _operation("operation-option-authorize", "authorize", "authorize(amount: Money): Authorization"),
            _operation("operation-option-settle", "settle", "settle(reference: String): void"),
        ]),
        n("class-digital-wallet", "class", "DigitalWallet", members=[
            _attribute("attribute-wallet-token", "token", "String"),
            _attribute("attribute-wallet-provider", "provider", "String"),
            _attribute("attribute-wallet-expiry", "expiresAt", "Date"),
        ]),
        n("class-wire-transfer", "class", "WireTransfer", members=[
            _attribute("attribute-wire-account", "accountNumber", "String"),
            _attribute("attribute-wire-holder", "accountHolder", "String"),
        ]),
        n("class-invoice", "class", "Invoice", members=[
            _attribute("attribute-invoice-id", "id", "String"),
            _attribute("attribute-invoice-issued", "issuedAt", "Date"),
            _attribute("attribute-invoice-total", "total", "Money"),
        ]),
        n("class-invoice-item", "class", "InvoiceItem", members=[
            _attribute("attribute-item-sku", "sku", "String"),
            _attribute("attribute-item-quantity", "quantity", "Int"),
            _attribute("attribute-item-price", "unitPrice", "Money"),
        ]),
        n("class-account", "class", "Account", members=[
            _attribute("attribute-account-id", "id", "String"),
            _attribute("attribute-account-name", "displayName", "String"),
            _attribute("attribute-account-email", "email", "String"),
        ]),
    ]
    relationships = [
        e("relation-service-uses-option", "class-billing-service", "interface-payment-option", "dependency", relation_kind="dependency"),
        e("relation-wallet-realizes-option", "class-digital-wallet", "interface-payment-option", "realization", relation_kind="realization"),
        e("relation-wire-realizes-option", "class-wire-transfer", "interface-payment-option", "realization", relation_kind="realization"),
        e("relation-invoice-owns-items", "class-invoice", "class-invoice-item", "composition", relation_kind="composition", source_multiplicity="1", target_multiplicity="1..*"),
        e("relation-invoice-belongs-account", "class-invoice", "class-account", "association", relation_kind="association", source_multiplicity="0..*", target_multiplicity="1"),
    ]
    ir = finalize("uml-class", nodes=containers, edges=relationships)
    ir["diagram"].update({
        "title": "Mô hình lớp thanh toán và hóa đơn",
        "detail": "faithful",
        "audience": "mixed",
    })
    ir["accessibility"].update({
        "name": "UML class cho thanh toán và hóa đơn",
        "description": "Bảy class và interface mô tả dịch vụ thanh toán, hai implementation, hóa đơn, dòng hóa đơn và tài khoản; năm connector phân biệt dependency, realization, composition và association.",
        "reading_order": [
            "class-billing-service", "operation-billing-charge",
            "interface-payment-option", "operation-option-authorize", "operation-option-settle",
            "class-digital-wallet", "attribute-wallet-token", "attribute-wallet-provider", "attribute-wallet-expiry",
            "class-wire-transfer", "attribute-wire-account", "attribute-wire-holder",
            "class-invoice", "attribute-invoice-id", "attribute-invoice-issued", "attribute-invoice-total",
            "class-invoice-item", "attribute-item-sku", "attribute-item-quantity", "attribute-item-price",
            "class-account", "attribute-account-id", "attribute-account-name", "attribute-account-email",
            "relation-service-uses-option", "relation-wallet-realizes-option", "relation-wire-realizes-option",
            "relation-invoice-owns-items", "relation-invoice-belongs-account",
        ],
    })
    for item in ir["source_items"]:
        item["locator"] = item["locator"].replace("fixture:", "D-104-original-illustrative:")
    return ir
