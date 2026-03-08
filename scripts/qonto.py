#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import os
import sys
from dataclasses import dataclass
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple
from urllib import error
from urllib import parse
from urllib import request


@dataclass(frozen=True)
class Parameter:
	name: str
	location: str
	query_name: str | None = None
	is_list: bool = False
	required: bool = False


@dataclass(frozen=True)
class Operation:
	name: str
	path: str
	description: str
	parameters: Tuple[Parameter, ...]


OPERATIONS: Dict[str, Operation] = {
	"get_qonto_attachment": Operation(
		name="get_qonto_attachment",
		path="/v2/attachments/{attachment_id}",
		description="Retrieve a single attachment.",
		parameters=(
			Parameter(name="attachment_id", location="path", required=True),
		),
	),
	"list_qonto_beneficiaries": Operation(
		name="list_qonto_beneficiaries",
		path="/v2/beneficiaries",
		description="List beneficiaries.",
		parameters=(
			Parameter(name="ibans", location="query", query_name="iban[]", is_list=True),
			Parameter(name="status", location="query", query_name="status[]", is_list=True),
			Parameter(name="trusted", location="query", query_name="trusted"),
			Parameter(name="updated_at_from", location="query", query_name="updated_at_from"),
			Parameter(name="updated_at_to", location="query", query_name="updated_at_to"),
			Parameter(name="page", location="query", query_name="page"),
			Parameter(name="per_page", location="query", query_name="per_page"),
			Parameter(name="sort_by", location="query", query_name="sort_by"),
		),
	),
	"get_qonto_beneficiary": Operation(
		name="get_qonto_beneficiary",
		path="/v2/beneficiaries/{beneficiary_id}",
		description="Retrieve one beneficiary.",
		parameters=(
			Parameter(name="beneficiary_id", location="path", required=True),
		),
	),
	"get_clients": Operation(
		name="get_clients",
		path="/v2/clients",
		description="List clients.",
		parameters=(
			Parameter(name="current_page", location="query", query_name="current_page"),
			Parameter(name="per_page", location="query", query_name="per_page"),
		),
	),
	"get_client": Operation(
		name="get_client",
		path="/v2/clients/{client_id}",
		description="Retrieve one client.",
		parameters=(
			Parameter(name="client_id", location="path", required=True),
		),
	),
	"get_client_invoices": Operation(
		name="get_client_invoices",
		path="/v2/client_invoices",
		description="List client invoices.",
		parameters=(
			Parameter(name="current_page", location="query", query_name="current_page"),
			Parameter(name="per_page", location="query", query_name="per_page"),
			Parameter(name="status", location="query", query_name="status"),
			Parameter(name="updated_at_from", location="query", query_name="updated_at_from"),
			Parameter(name="updated_at_to", location="query", query_name="updated_at_to"),
		),
	),
	"get_supplier_invoices": Operation(
		name="get_supplier_invoices",
		path="/v2/supplier_invoices",
		description="List supplier invoices.",
		parameters=(
			Parameter(name="current_page", location="query", query_name="current_page"),
			Parameter(name="per_page", location="query", query_name="per_page"),
			Parameter(name="status", location="query", query_name="status"),
			Parameter(name="updated_at_from", location="query", query_name="updated_at_from"),
			Parameter(name="updated_at_to", location="query", query_name="updated_at_to"),
		),
	),
	"get_credit_notes": Operation(
		name="get_credit_notes",
		path="/v2/credit_notes",
		description="List credit notes.",
		parameters=(
			Parameter(name="current_page", location="query", query_name="current_page"),
			Parameter(name="per_page", location="query", query_name="per_page"),
			Parameter(name="updated_at_from", location="query", query_name="updated_at_from"),
			Parameter(name="updated_at_to", location="query", query_name="updated_at_to"),
		),
	),
	"list_qonto_labels": Operation(
		name="list_qonto_labels",
		path="/v2/labels",
		description="List labels.",
		parameters=(
			Parameter(name="page", location="query", query_name="page"),
			Parameter(name="per_page", location="query", query_name="per_page"),
		),
	),
	"get_qonto_label": Operation(
		name="get_qonto_label",
		path="/v2/labels/{label_id}",
		description="Retrieve one label.",
		parameters=(
			Parameter(name="label_id", location="path", required=True),
		),
	),
	"list_qonto_memberships": Operation(
		name="list_qonto_memberships",
		path="/v2/memberships",
		description="List memberships.",
		parameters=(
			Parameter(name="page", location="query", query_name="page"),
			Parameter(name="per_page", location="query", query_name="per_page"),
		),
	),
	"get_qonto_organization": Operation(
		name="get_qonto_organization",
		path="/v2/organization",
		description="Retrieve organization and bank accounts.",
		parameters=(),
	),
	"get_requests": Operation(
		name="get_requests",
		path="/v2/requests",
		description="List approval requests.",
		parameters=(
			Parameter(name="current_page", location="query", query_name="current_page"),
			Parameter(name="per_page", location="query", query_name="per_page"),
			Parameter(name="status", location="query", query_name="status"),
			Parameter(name="updated_at_from", location="query", query_name="updated_at_from"),
			Parameter(name="updated_at_to", location="query", query_name="updated_at_to"),
		),
	),
	"get_request": Operation(
		name="get_request",
		path="/v2/requests/{request_id}",
		description="Retrieve one approval request.",
		parameters=(
			Parameter(name="request_id", location="path", required=True),
		),
	),
	"get_statements": Operation(
		name="get_statements",
		path="/v2/statements",
		description="List statements.",
		parameters=(
			Parameter(name="current_page", location="query", query_name="current_page"),
			Parameter(name="per_page", location="query", query_name="per_page"),
			Parameter(name="created_at_from", location="query", query_name="created_at_from"),
			Parameter(name="created_at_to", location="query", query_name="created_at_to"),
		),
	),
	"download_statement": Operation(
		name="download_statement",
		path="/v2/statements/{statement_id}/download",
		description="Retrieve one statement download payload.",
		parameters=(
			Parameter(name="statement_id", location="path", required=True),
		),
	),
	"list_qonto_transaction_attachments": Operation(
		name="list_qonto_transaction_attachments",
		path="/v2/transactions/{transaction_id}/attachments",
		description="List attachments for one transaction.",
		parameters=(
			Parameter(name="transaction_id", location="path", required=True),
			Parameter(name="page", location="query", query_name="page"),
			Parameter(name="per_page", location="query", query_name="per_page"),
		),
	),
	"get_qonto_transactions": Operation(
		name="get_qonto_transactions",
		path="/v2/transactions",
		description="List transactions for one bank account.",
		parameters=(
			Parameter(name="bank_account_id", location="query", query_name="bank_account_id", required=True),
		),
	),
	"get_qonto_transaction": Operation(
		name="get_qonto_transaction",
		path="/v2/transactions/{transaction_id}",
		description="Retrieve one transaction.",
		parameters=(
			Parameter(name="transaction_id", location="path", required=True),
			Parameter(name="includes", location="query", query_name="includes[]", is_list=True),
		),
	),
	"get_qonto_external_transfer": Operation(
		name="get_qonto_external_transfer",
		path="/v2/external_transfers/{transfer_id}",
		description="Retrieve one external transfer.",
		parameters=(
			Parameter(name="transfer_id", location="path", required=True),
		),
	),
	"list_qonto_external_transfers": Operation(
		name="list_qonto_external_transfers",
		path="/v2/external_transfers",
		description="List external transfers.",
		parameters=(
			Parameter(name="scheduled_date_from", location="query", query_name="scheduled_date_from"),
			Parameter(name="scheduled_date_to", location="query", query_name="scheduled_date_to"),
			Parameter(name="updated_at_from", location="query", query_name="updated_at_from"),
			Parameter(name="updated_at_to", location="query", query_name="updated_at_to"),
			Parameter(name="beneficiary_ids", location="query", query_name="beneficiary_ids[]", is_list=True),
			Parameter(name="page", location="query", query_name="page"),
			Parameter(name="per_page", location="query", query_name="per_page"),
			Parameter(name="sort_by", location="query", query_name="sort_by"),
			Parameter(name="status", location="query", query_name="status[]", is_list=True),
		),
	),
}


def main() -> int:
	parser = build_parser()
	args = parser.parse_args()

	if args.command == "list-operations":
		return list_operations()

	if args.command == "describe":
		return describe_operation(args.operation)

	if args.command == "call":
		return call_operation(args.operation, args.params)

	parser.print_help()
	return 1


def build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(description="Read-only Qonto API helper.")
	subparsers = parser.add_subparsers(dest="command")

	subparsers.add_parser("list-operations", help="List supported operations.")

	describe_parser = subparsers.add_parser("describe", help="Describe one operation.")
	describe_parser.add_argument("operation")

	call_parser = subparsers.add_parser("call", help="Execute one operation.")
	call_parser.add_argument("operation")
	call_parser.add_argument("--params", default="{}", help="JSON object with operation parameters.")

	return parser


def list_operations() -> int:
	items = []

	for operation in OPERATIONS.values():
		items.append(
			{
				"name": operation.name,
				"description": operation.description,
			}
		)

	print_json(items)
	return 0


def describe_operation(operation_name: str) -> int:
	operation = OPERATIONS.get(operation_name)

	if operation is None:
		return print_cli_error(f"Unknown operation: {operation_name}")

	parameters = []

	for parameter in operation.parameters:
		parameters.append(
			{
				"name": parameter.name,
				"location": parameter.location,
				"query_name": parameter.query_name,
				"is_list": parameter.is_list,
				"required": parameter.required,
			}
		)

	print_json(
		{
			"name": operation.name,
			"description": operation.description,
			"path": operation.path,
			"parameters": parameters,
		}
	)
	return 0


def call_operation(operation_name: str, raw_params: str) -> int:
	operation = OPERATIONS.get(operation_name)

	if operation is None:
		return print_cli_error(f"Unknown operation: {operation_name}")

	try:
		input_params = json.loads(raw_params)
	except json.JSONDecodeError as exc:
		return print_cli_error(f"Invalid JSON for --params: {exc.msg}")

	if isinstance(input_params, dict) is False:
		return print_cli_error("--params must decode to a JSON object.")

	try:
		normalized_params = normalize_params(operation, input_params)
		url, request_payload = build_request(operation, normalized_params)
		response_payload = perform_request(url)
	except QontoError as exc:
		print_json(
			{
				"ok": False,
				"operation": operation.name,
				"request": exc.request_payload,
				"error": exc.error_payload,
			}
		)
		return 1

	print_json(
		{
			"ok": True,
			"operation": operation.name,
			"request": request_payload,
			"data": response_payload,
		}
	)
	return 0


def normalize_params(operation: Operation, input_params: Dict[str, Any]) -> Dict[str, Any]:
	allowed_names = {parameter.name for parameter in operation.parameters}
	unknown_names = sorted(set(input_params.keys()) - allowed_names)

	if len(unknown_names) > 0:
		raise QontoError(
			request_payload={},
			error_payload={
				"type": "validation_error",
				"message": f"Unknown parameters: {', '.join(unknown_names)}",
			},
		)

	normalized_params: Dict[str, Any] = {}

	for parameter in operation.parameters:
		value = input_params.get(parameter.name)

		if value is None:
			if parameter.required is True:
				raise QontoError(
					request_payload={},
					error_payload={
						"type": "validation_error",
						"message": f"Missing required parameter: {parameter.name}",
					},
				)

			continue

		if parameter.is_list is True:
			normalized_params[parameter.name] = normalize_list_value(parameter.name, value)
			continue

		if isinstance(value, list) is True:
			raise QontoError(
				request_payload={},
				error_payload={
					"type": "validation_error",
					"message": f"Parameter must not be a list: {parameter.name}",
				},
			)

		normalized_params[parameter.name] = value

	return normalized_params


def normalize_list_value(parameter_name: str, value: Any) -> List[Any]:
	if isinstance(value, list) is True:
		return value

	if value is None:
		return []

	if isinstance(value, bool) is True:
		return [value]

	if isinstance(value, tuple) is True:
		return list(value)

	if isinstance(value, str) is True:
		return [value]

	if isinstance(value, int) is True:
		return [value]

	if isinstance(value, float) is True:
		return [value]

	raise QontoError(
		request_payload={},
		error_payload={
			"type": "validation_error",
			"message": f"Unsupported list value for parameter: {parameter_name}",
		},
	)


def build_request(operation: Operation, normalized_params: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
	host = os.getenv("QONTO_THIRDPARTY_HOST", "https://thirdparty.qonto.com").rstrip("/")
	path = operation.path

	for parameter in operation.parameters:
		if parameter.location != "path":
			continue

		value = normalized_params.get(parameter.name)

		if value is None:
			continue

		path = path.replace("{" + parameter.name + "}", parse.quote(str(value), safe=""))

	query_items: List[Tuple[str, str]] = []
	query_payload: Dict[str, Any] = {}

	for parameter in operation.parameters:
		if parameter.location != "query":
			continue

		value = normalized_params.get(parameter.name)

		if value is None:
			continue

		if parameter.is_list is True:
			for item in value:
				query_key = parameter.query_name or parameter.name
				query_value = stringify_query_value(item)
				query_items.append((query_key, query_value))
				existing_query_values = query_payload.get(query_key)

				if existing_query_values is None:
					query_payload[query_key] = [query_value]
					continue

				existing_query_values.append(query_value)

			continue

		query_key = parameter.query_name or parameter.name
		query_value = stringify_query_value(value)
		query_items.append((query_key, query_value))
		query_payload[query_key] = query_value

	query_string = parse.urlencode(query_items, doseq=True)
	url = f"{host}{path}"

	if len(query_string) > 0:
		url = f"{url}?{query_string}"

	request_payload = {
		"method": "GET",
		"url": url,
		"path": path,
		"query": query_payload,
	}

	return url, request_payload


def stringify_query_value(value: Any) -> str:
	if isinstance(value, bool) is True:
		if value is True:
			return "true"

		return "false"

	if isinstance(value, str) is True:
		return value

	if isinstance(value, int) is True:
		return str(value)

	if isinstance(value, float) is True:
		return str(value)

	return json.dumps(value, separators=(",", ":"))


def perform_request(url: str) -> Any:
	headers = build_headers()
	http_request = request.Request(url=url, method="GET", headers=headers)

	try:
		with request.urlopen(http_request) as response:
			status = response.status
			body = response.read().decode("utf-8")
			payload = parse_response_body(body)

			if 200 <= status < 300:
				return payload

			raise QontoError(
				request_payload={"method": "GET", "url": url},
				error_payload={
					"type": "http_error",
					"status": status,
					"message": f"Qonto returned status {status}",
					"body": payload,
				},
			)
	except error.HTTPError as exc:
		body = exc.read().decode("utf-8")
		payload = parse_response_body(body)
		raise QontoError(
			request_payload={"method": "GET", "url": url},
			error_payload={
				"type": "http_error",
				"status": exc.code,
				"message": exc.reason,
				"body": payload,
			},
		) from exc
	except error.URLError as exc:
		raise QontoError(
			request_payload={"method": "GET", "url": url},
			error_payload={
				"type": "network_error",
				"message": str(exc.reason),
			},
		) from exc


def build_headers() -> Dict[str, str]:
	api_key = os.getenv("QONTO_API_KEY")
	organization_id = os.getenv("QONTO_ORGANIZATION_ID")
	staging_token = os.getenv("QONTO_STAGING_TOKEN")

	if api_key is None:
		raise QontoError(
			request_payload={},
			error_payload={
				"type": "configuration_error",
				"message": "QONTO_API_KEY is not set.",
			},
		)

	if organization_id is None:
		raise QontoError(
			request_payload={},
			error_payload={
				"type": "configuration_error",
				"message": "QONTO_ORGANIZATION_ID is not set.",
			},
		)

	headers = {
		"Accept": "application/json",
		"Authorization": f"{organization_id}:{api_key}",
	}

	if staging_token is not None:
		headers["X-Qonto-Staging-Token"] = staging_token

	return headers


def parse_response_body(body: str) -> Any:
	if len(body) == 0:
		return None

	try:
		return json.loads(body)
	except json.JSONDecodeError:
		return body


def print_cli_error(message: str) -> int:
	print_json(
		{
			"ok": False,
			"error": {
				"type": "cli_error",
				"message": message,
			},
		}
	)
	return 1


def print_json(payload: Any) -> None:
	json.dump(payload, sys.stdout, indent=2, sort_keys=True)
	sys.stdout.write("\n")


class QontoError(Exception):
	def __init__(self, request_payload: Dict[str, Any], error_payload: Dict[str, Any]) -> None:
		super().__init__(error_payload.get("message", "Qonto request failed."))
		self.request_payload = request_payload
		self.error_payload = error_payload


if __name__ == "__main__":
	raise SystemExit(main())
