#!/usr/bin/env bash
set -euo pipefail

readonly OPERATIONS_JSON=$(cat <<'EOF'
{
  "get_qonto_attachment": {
    "description": "Retrieve a single attachment.",
    "path": "/v2/attachments/{attachment_id}",
    "parameters": [
      { "name": "attachment_id", "location": "path", "required": true }
    ]
  },
  "list_qonto_beneficiaries": {
    "description": "List beneficiaries.",
    "path": "/v2/beneficiaries",
    "parameters": [
      { "name": "ibans", "location": "query", "query_name": "iban[]", "is_list": true },
      { "name": "status", "location": "query", "query_name": "status[]", "is_list": true },
      { "name": "trusted", "location": "query", "query_name": "trusted" },
      { "name": "updated_at_from", "location": "query", "query_name": "updated_at_from" },
      { "name": "updated_at_to", "location": "query", "query_name": "updated_at_to" },
      { "name": "page", "location": "query", "query_name": "page" },
      { "name": "per_page", "location": "query", "query_name": "per_page" },
      { "name": "sort_by", "location": "query", "query_name": "sort_by" }
    ]
  },
  "get_qonto_beneficiary": {
    "description": "Retrieve one beneficiary.",
    "path": "/v2/beneficiaries/{beneficiary_id}",
    "parameters": [
      { "name": "beneficiary_id", "location": "path", "required": true }
    ]
  },
  "get_clients": {
    "description": "List clients.",
    "path": "/v2/clients",
    "parameters": [
      { "name": "current_page", "location": "query", "query_name": "current_page" },
      { "name": "per_page", "location": "query", "query_name": "per_page" }
    ]
  },
  "get_client": {
    "description": "Retrieve one client.",
    "path": "/v2/clients/{client_id}",
    "parameters": [
      { "name": "client_id", "location": "path", "required": true }
    ]
  },
  "get_client_invoices": {
    "description": "List client invoices.",
    "path": "/v2/client_invoices",
    "parameters": [
      { "name": "current_page", "location": "query", "query_name": "current_page" },
      { "name": "per_page", "location": "query", "query_name": "per_page" },
      { "name": "status", "location": "query", "query_name": "status" },
      { "name": "updated_at_from", "location": "query", "query_name": "updated_at_from" },
      { "name": "updated_at_to", "location": "query", "query_name": "updated_at_to" }
    ]
  },
  "get_supplier_invoices": {
    "description": "List supplier invoices.",
    "path": "/v2/supplier_invoices",
    "parameters": [
      { "name": "current_page", "location": "query", "query_name": "current_page" },
      { "name": "per_page", "location": "query", "query_name": "per_page" },
      { "name": "status", "location": "query", "query_name": "status" },
      { "name": "updated_at_from", "location": "query", "query_name": "updated_at_from" },
      { "name": "updated_at_to", "location": "query", "query_name": "updated_at_to" }
    ]
  },
  "get_credit_notes": {
    "description": "List credit notes.",
    "path": "/v2/credit_notes",
    "parameters": [
      { "name": "current_page", "location": "query", "query_name": "current_page" },
      { "name": "per_page", "location": "query", "query_name": "per_page" },
      { "name": "updated_at_from", "location": "query", "query_name": "updated_at_from" },
      { "name": "updated_at_to", "location": "query", "query_name": "updated_at_to" }
    ]
  },
  "list_qonto_labels": {
    "description": "List labels.",
    "path": "/v2/labels",
    "parameters": [
      { "name": "page", "location": "query", "query_name": "page" },
      { "name": "per_page", "location": "query", "query_name": "per_page" }
    ]
  },
  "get_qonto_label": {
    "description": "Retrieve one label.",
    "path": "/v2/labels/{label_id}",
    "parameters": [
      { "name": "label_id", "location": "path", "required": true }
    ]
  },
  "list_qonto_memberships": {
    "description": "List memberships.",
    "path": "/v2/memberships",
    "parameters": [
      { "name": "page", "location": "query", "query_name": "page" },
      { "name": "per_page", "location": "query", "query_name": "per_page" }
    ]
  },
  "get_qonto_organization": {
    "description": "Retrieve organization and bank accounts.",
    "path": "/v2/organization",
    "parameters": []
  },
  "get_requests": {
    "description": "List approval requests.",
    "path": "/v2/requests",
    "parameters": [
      { "name": "current_page", "location": "query", "query_name": "current_page" },
      { "name": "per_page", "location": "query", "query_name": "per_page" },
      { "name": "status", "location": "query", "query_name": "status" },
      { "name": "updated_at_from", "location": "query", "query_name": "updated_at_from" },
      { "name": "updated_at_to", "location": "query", "query_name": "updated_at_to" }
    ]
  },
  "get_request": {
    "description": "Retrieve one approval request.",
    "path": "/v2/requests/{request_id}",
    "parameters": [
      { "name": "request_id", "location": "path", "required": true }
    ]
  },
  "get_statements": {
    "description": "List statements.",
    "path": "/v2/statements",
    "parameters": [
      { "name": "current_page", "location": "query", "query_name": "current_page" },
      { "name": "per_page", "location": "query", "query_name": "per_page" },
      { "name": "created_at_from", "location": "query", "query_name": "created_at_from" },
      { "name": "created_at_to", "location": "query", "query_name": "created_at_to" }
    ]
  },
  "download_statement": {
    "description": "Retrieve one statement download payload.",
    "path": "/v2/statements/{statement_id}/download",
    "parameters": [
      { "name": "statement_id", "location": "path", "required": true }
    ]
  },
  "list_qonto_transaction_attachments": {
    "description": "List attachments for one transaction.",
    "path": "/v2/transactions/{transaction_id}/attachments",
    "parameters": [
      { "name": "transaction_id", "location": "path", "required": true },
      { "name": "page", "location": "query", "query_name": "page" },
      { "name": "per_page", "location": "query", "query_name": "per_page" }
    ]
  },
  "get_qonto_transactions": {
    "description": "List transactions for one bank account with pagination, sorting, and date filters.",
    "path": "/v2/transactions",
    "parameters": [
      { "name": "bank_account_id", "location": "query", "query_name": "bank_account_id", "required": true },
      { "name": "page", "location": "query", "query_name": "current_page" },
      { "name": "current_page", "location": "query", "query_name": "current_page" },
      { "name": "per_page", "location": "query", "query_name": "per_page" },
      { "name": "updated_at_from", "location": "query", "query_name": "updated_at_from" },
      { "name": "updated_at_to", "location": "query", "query_name": "updated_at_to" },
      { "name": "emitted_at_from", "location": "query", "query_name": "emitted_at_from" },
      { "name": "emitted_at_to", "location": "query", "query_name": "emitted_at_to" },
      { "name": "settled_at_from", "location": "query", "query_name": "settled_at_from" },
      { "name": "settled_at_to", "location": "query", "query_name": "settled_at_to" },
      { "name": "sort_by", "location": "query", "query_name": "sort_by" }
    ]
  },
  "get_qonto_transaction": {
    "description": "Retrieve one transaction.",
    "path": "/v2/transactions/{transaction_id}",
    "parameters": [
      { "name": "transaction_id", "location": "path", "required": true },
      { "name": "includes", "location": "query", "query_name": "includes[]", "is_list": true }
    ]
  },
  "get_qonto_external_transfer": {
    "description": "Retrieve one external transfer.",
    "path": "/v2/external_transfers/{transfer_id}",
    "parameters": [
      { "name": "transfer_id", "location": "path", "required": true }
    ]
  },
  "list_qonto_external_transfers": {
    "description": "List external transfers.",
    "path": "/v2/external_transfers",
    "parameters": [
      { "name": "scheduled_date_from", "location": "query", "query_name": "scheduled_date_from" },
      { "name": "scheduled_date_to", "location": "query", "query_name": "scheduled_date_to" },
      { "name": "updated_at_from", "location": "query", "query_name": "updated_at_from" },
      { "name": "updated_at_to", "location": "query", "query_name": "updated_at_to" },
      { "name": "beneficiary_ids", "location": "query", "query_name": "beneficiary_ids[]", "is_list": true },
      { "name": "page", "location": "query", "query_name": "page" },
      { "name": "per_page", "location": "query", "query_name": "per_page" },
      { "name": "sort_by", "location": "query", "query_name": "sort_by" },
      { "name": "status", "location": "query", "query_name": "status[]", "is_list": true }
    ]
  }
}
EOF
)

main() {
	require_binary curl
	require_binary jq

	local command="${1:-}"

	if [ -z "$command" ]; then
		print_cli_error "Missing command."
		return 1
	fi

	if [ "$command" = "list-operations" ]; then
		list_operations
		return 0
	fi

	if [ "$command" = "describe" ]; then
		describe_operation "${2:-}"
		return $?
	fi

	if [ "$command" = "call" ]; then
		call_operation "$@"
		return $?
	fi

	print_cli_error "Unknown command: $command"
	return 1
}

require_binary() {
	local binary_name="$1"

	if command -v "$binary_name" >/dev/null 2>&1; then
		return 0
	fi

	print_cli_error "Missing required binary: $binary_name"
	exit 1
}

list_operations() {
	printf '%s\n' "$OPERATIONS_JSON" | jq 'to_entries | map({name: .key, description: .value.description})'
}

describe_operation() {
	local operation_name="${1:-}"
	local operation_json

	if [ -z "$operation_name" ]; then
		print_cli_error "Missing operation name."
		return 1
	fi

	operation_json="$(get_operation_json "$operation_name")"

	if [ -z "$operation_json" ]; then
		print_cli_error "Unknown operation: $operation_name"
		return 1
	fi

	jq -n \
		--arg operation_name "$operation_name" \
		--argjson operation "$operation_json" \
		'{
			name: $operation_name,
			description: $operation.description,
			path: $operation.path,
			parameters: ($operation.parameters // [])
		}'
}

call_operation() {
	local operation_name="${2:-}"
	local params_json='{}'
	local operation_json
	local request_json
	local url
	local status
	local body_file
	local error_file
	local body_payload
	local configuration_error_json

	if [ -z "$operation_name" ]; then
		print_cli_error "Missing operation name."
		return 1
	fi

	shift 2

	while [ "$#" -gt 0 ]; do
		if [ "$1" = "--params" ]; then
			if [ "$#" -lt 2 ]; then
				print_cli_error "Missing value for --params."
				return 1
			fi

			params_json="$2"
			shift 2
			continue
		fi

		print_cli_error "Unknown argument: $1"
		return 1
	done

	operation_json="$(get_operation_json "$operation_name")"

	if [ -z "$operation_json" ]; then
		print_cli_error "Unknown operation: $operation_name"
		return 1
	fi

	if jq -e 'type == "object"' >/dev/null 2>&1 <<<"$params_json"; then
		true
	else
		print_cli_error "--params must decode to a JSON object."
		return 1
	fi

	request_json="$(build_request_json "$operation_name" "$operation_json" "$params_json")"

	if jq -e '.ok == true' >/dev/null 2>&1 <<<"$request_json"; then
		true
	else
		print_operation_error "$operation_name" '{}' "$(jq -c '.error' <<<"$request_json")"
		return 1
	fi

	url="$(jq -r '.url' <<<"$request_json")"
	configuration_error_json="$(get_configuration_error_json)"

	if [ -z "$configuration_error_json" ]; then
		true
	else
		print_operation_error "$operation_name" "$(jq -c '.request' <<<"$request_json")" "$configuration_error_json"
		return 1
	fi

	body_file="$(mktemp)"
	error_file="$(mktemp)"

	if status="$(perform_request "$url" "$body_file" "$error_file")"; then
		true
	else
		print_operation_error "$operation_name" "$(jq -c '.request' <<<"$request_json")" "$(jq -cn --rawfile error_file "$error_file" '{type: "network_error", message: ($error_file | rtrimstr("\n"))}')"
		rm -f "$body_file" "$error_file"
		return 1
	fi

	body_payload="$(parse_body_payload "$body_file")"

	if [ "$status" -ge 200 ] && [ "$status" -lt 300 ]; then
		jq -n \
			--arg operation "$operation_name" \
			--argjson request "$(jq -c '.request' <<<"$request_json")" \
			--argjson data "$body_payload" \
			'{
				ok: true,
				operation: $operation,
				request: $request,
				data: $data
			}'
		rm -f "$body_file" "$error_file"
		return 0
	fi

	print_operation_error "$operation_name" "$(jq -c '.request' <<<"$request_json")" "$(jq -cn --argjson body "$body_payload" --arg status "$status" '{type: "http_error", status: ($status | tonumber), message: ("Qonto returned status " + $status), body: $body}')"
	rm -f "$body_file" "$error_file"
	return 1
}

get_operation_json() {
	local operation_name="$1"

	printf '%s\n' "$OPERATIONS_JSON" | jq -c --arg operation_name "$operation_name" '.[$operation_name] // empty'
}

build_request_json() {
	local operation_name="$1"
	local operation_json="$2"
	local params_json="$3"
	local host
	local unknown_names
	local supported_names
	local missing_names
	local path
	local query_payload='{}'
	local query_pairs=()
	local parameter_rows
	local parameter_row
	local parameter_json
	local name
	local location
	local is_list
	local required
	local query_name
	local value_type
	local string_value

	host="$(get_host)"
	unknown_names="$(jq -r --argjson operation "$operation_json" '((keys_unsorted - ($operation.parameters | map(.name)))[])?' <<<"$params_json")"
	supported_names="$(jq -r --argjson operation "$operation_json" '($operation.parameters // []) | map(.name) | join(", ")' <<<"$params_json")"

	if [ -n "$unknown_names" ]; then
		jq -n --arg message "Unknown parameters: $(join_lines "$unknown_names"). Supported parameters: ${supported_names}" '{ok: false, error: {type: "validation_error", message: $message}}'
		return 0
	fi

	missing_names="$(jq -r --argjson operation "$operation_json" '. as $params | [ $operation.parameters[] | select((.required // false) == true and $params[.name] == null) | .name ][]?' <<<"$params_json")"

	if [ -n "$missing_names" ]; then
		jq -n --arg message "Missing required parameter: $(join_lines "$missing_names")" '{ok: false, error: {type: "validation_error", message: $message}}'
		return 0
	fi

	path="$(jq -r '.path' <<<"$operation_json")"
	parameter_rows="$(jq -cr '.parameters[]?' <<<"$operation_json")"

	while IFS= read -r parameter_row; do
		if [ -z "$parameter_row" ]; then
			continue
		fi

		parameter_json="$parameter_row"
		name="$(jq -r '.name' <<<"$parameter_json")"
		location="$(jq -r '.location' <<<"$parameter_json")"
		is_list="$(jq -r '(.is_list // false)' <<<"$parameter_json")"
		required="$(jq -r '(.required // false)' <<<"$parameter_json")"
		query_name="$(jq -r '(.query_name // .name)' <<<"$parameter_json")"

		if jq -e --arg name "$name" '.[$name] != null' >/dev/null 2>&1 <<<"$params_json"; then
			true
		else
			if [ "$required" = "true" ]; then
				jq -n --arg message "Missing required parameter: $name" '{ok: false, error: {type: "validation_error", message: $message}}'
				return 0
			fi

			continue
		fi

		value_type="$(jq -r --arg name "$name" '.[$name] | type' <<<"$params_json")"

		if [ "$location" = "path" ]; then
			if [ "$value_type" = "array" ]; then
				jq -n --arg message "Parameter must not be a list: $name" '{ok: false, error: {type: "validation_error", message: $message}}'
				return 0
			fi

			string_value="$(jq -r --arg name "$name" 'if .[$name] == true then "true" elif .[$name] == false then "false" else .[$name] | tostring end' <<<"$params_json")"
			path="${path//\{$name\}/$(uri_encode "$string_value")}"
			continue
		fi

		if [ "$is_list" = "true" ]; then
			if [ "$value_type" = "array" ]; then
				while IFS= read -r string_value; do
					query_payload="$(jq -c --arg key "$query_name" --arg value "$string_value" '.[$key] = ((.[$key] // []) + [$value])' <<<"$query_payload")"
					query_pairs+=("$(build_query_pair "$query_name" "$string_value")")
				done < <(jq -r --arg name "$name" '.[$name][] | if . == true then "true" elif . == false then "false" else tostring end' <<<"$params_json")
				continue
			fi

			string_value="$(jq -r --arg name "$name" 'if .[$name] == true then "true" elif .[$name] == false then "false" else .[$name] | tostring end' <<<"$params_json")"
			query_payload="$(jq -c --arg key "$query_name" --arg value "$string_value" '.[$key] = ((.[$key] // []) + [$value])' <<<"$query_payload")"
			query_pairs+=("$(build_query_pair "$query_name" "$string_value")")
			continue
		fi

		if [ "$value_type" = "array" ]; then
			jq -n --arg message "Parameter must not be a list: $name" '{ok: false, error: {type: "validation_error", message: $message}}'
			return 0
		fi

		string_value="$(jq -r --arg name "$name" 'if .[$name] == true then "true" elif .[$name] == false then "false" else .[$name] | tostring end' <<<"$params_json")"
		query_payload="$(jq -c --arg key "$query_name" --arg value "$string_value" '. + {($key): $value}' <<<"$query_payload")"
		query_pairs+=("$(build_query_pair "$query_name" "$string_value")")
	done <<<"$parameter_rows"

	jq -n \
		--arg host "$host" \
		--arg path "$path" \
		--arg query_string "$(join_query_pairs "${query_pairs[@]:-}")" \
		--argjson query_payload "$query_payload" \
		'{
			ok: true,
			url: (
				if ($query_string | length) > 0 then
					$host + $path + "?" + $query_string
				else
					$host + $path
				end
			),
			request: {
				method: "GET",
				url: (
					if ($query_string | length) > 0 then
						$host + $path + "?" + $query_string
					else
						$host + $path
					end
				),
				path: $path,
				query: $query_payload
			}
		}'
}

perform_request() {
	local url="$1"
	local body_file="$2"
	local error_file="$3"
	local auth_header

	auth_header="$(build_auth_header)"

	if [ -n "${QONTO_STAGING_TOKEN:-}" ]; then
		curl -sS -o "$body_file" -w '%{http_code}' \
			-H 'Accept: application/json' \
			-H "Authorization: $auth_header" \
			-H "X-Qonto-Staging-Token: ${QONTO_STAGING_TOKEN}" \
			"$url" 2>"$error_file"
		return $?
	fi

	curl -sS -o "$body_file" -w '%{http_code}' \
		-H 'Accept: application/json' \
		-H "Authorization: $auth_header" \
		"$url" 2>"$error_file"
	return $?
}

build_auth_header() {
	local api_key="${QONTO_API_KEY:-}"
	local organization_id="${QONTO_ORGANIZATION_ID:-}"

	printf '%s' "${organization_id}:${api_key}"
}

get_configuration_error_json() {
	local api_key="${QONTO_API_KEY:-}"
	local organization_id="${QONTO_ORGANIZATION_ID:-}"

	if [ -z "$api_key" ]; then
		jq -cn '{type: "configuration_error", message: "QONTO_API_KEY is not set."}'
		return 0
	fi

	if [ -z "$organization_id" ]; then
		jq -cn '{type: "configuration_error", message: "QONTO_ORGANIZATION_ID is not set."}'
		return 0
	fi

	printf '%s' ''
}

get_host() {
	printf '%s' "${QONTO_THIRDPARTY_HOST:-https://thirdparty.qonto.com}" | sed 's#/$##'
}

join_query_pairs() {
	local pairs=("$@")
	local index=0
	local joined=''

	while [ "$index" -lt "${#pairs[@]}" ]; do
		if [ "$index" -gt 0 ]; then
			joined="${joined}&"
		fi

		joined="${joined}${pairs[$index]}"
		index=$((index + 1))
	done

	printf '%s' "$joined"
}

join_lines() {
	printf '%s\n' "$1" | jq -Rsc 'split("\n") | map(select(length > 0)) | join(", ")' | jq -r .
}

build_query_pair() {
	local key="$1"
	local value="$2"

	printf '%s=%s' "$(uri_encode "$key")" "$(uri_encode "$value")"
}

uri_encode() {
	printf '%s' "$1" | jq -sRr @uri
}

parse_body_payload() {
	local body_file="$1"

	if jq -e . >/dev/null 2>&1 <"$body_file"; then
		jq -c . <"$body_file"
		return 0
	fi

	jq -Rs . <"$body_file"
}

print_cli_error() {
	local message="$1"

	jq -n --arg message "$message" '{ok: false, error: {type: "cli_error", message: $message}}'
}

print_operation_error() {
	local operation_name="$1"
	local request_json="$2"
	local error_json="$3"

	jq -n \
		--arg operation "$operation_name" \
		--argjson request "$request_json" \
		--argjson error "$error_json" \
		'{
			ok: false,
			operation: $operation,
			request: $request,
			error: $error
		}'
}

main "$@"
