#!/bin/bash

# ANSI color codes for green and red
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Função para normalizar strings removendo espaços, novas linhas, "n" e aspas escapadas
normalize_response() {
    echo "$1" | tr -d '\n' | sed -e 's/\\n//g' -e 's/\\"/"/g' -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//'
}

# ----------- TESTS FOR compare_hashes FUNCTION -----------

# Test compare_hashes function with equal hashes
RESPONSE=$(dfx canister call blockchain-integridad-backend compare_hashes '("abc123", "abc123")')
if [[ "$RESPONSE" == *"ok = \"Same document\""* ]]; then
    echo -e "${GREEN}Test passed: Same document${NC}"
else
    echo -e "${RED}Test failed: Expected ok = \"Same document\" but got $RESPONSE${NC}"
    exit 1
fi

# Test compare_hashes function with different hashes
RESPONSE=$(dfx canister call blockchain-integridad-backend compare_hashes '("abc123", "xyz789")')
if [[ "$RESPONSE" == *"err = \"Different documents\""* ]]; then
    echo -e "${GREEN}Test passed: Different documents${NC}"
else
    echo -e "${RED}Test failed: Expected err = \"Different documents\" but got $RESPONSE${NC}"
    exit 1
fi

# ----------- TESTS FOR get_raw_data FUNCTION -----------

# Test get_raw_data function with a valid URL
VALID_URL="https://raw.githubusercontent.com/Inteli-College/2024-2B-T09-ES08-G02/refs/heads/main/src/blockchain-integridad/src/data/equal1.json?token=GHSAT0AAAAAAC24GFCEPQPPI6LPW76EJRPEZ2RXFNQ"
EXPECTED_CONTENT='{
  "s3_url": "www.example.com",
  "s3_previous_url": "www.example.com",
  "content": "poggers"
}'

RESPONSE=$(dfx canister call blockchain-integridad-backend get_raw_data "(\"$VALID_URL\")")
NORMALIZED_RESPONSE=$(normalize_response "$RESPONSE")
NORMALIZED_EXPECTED=$(normalize_response "$EXPECTED_CONTENT")

if [[ "$NORMALIZED_RESPONSE" == *"$NORMALIZED_EXPECTED"* ]]; then
    echo -e "${GREEN}Test passed: get_raw_data with valid URL${NC}"
else
    echo -e "${RED}Test failed: Expected response to contain sample content but got $NORMALIZED_RESPONSE${NC}"
    exit 1
fi

# ----------- TESTS FOR get_stable_raw_json FUNCTION -----------

# Test get_stable_raw_json function after a call to get_raw_data
RESPONSE=$(dfx canister call blockchain-integridad-backend get_stable_raw_json)
NORMALIZED_RESPONSE=$(normalize_response "$RESPONSE")

if [[ "$NORMALIZED_RESPONSE" == *"$NORMALIZED_EXPECTED"* ]]; then
    echo -e "${GREEN}Test passed: get_stable_raw_json after get_raw_data${NC}"
else
    echo -e "${RED}Test failed: Expected response to contain sample content but got $NORMALIZED_RESPONSE${NC}"
    exit 1
fi

# ----------- TESTS FOR send_post_request FUNCTION -----------

# Test send_post_request function with valid URL and JSON body
POST_URL="https://127.0.0.1:5000/upload"
POST_BODY='{\"username\": \"raissa\", \"password\": \"0\", \"project\": [\"Inteli\"], \"key\": \"arquivo.json\", \"content\": \"{\\\"data\\\": \\\"Exemplo de conteúdo JSON\\\"}\"}'
EXPECTED_POST_RESPONSE="expected server response"

RESPONSE=$(dfx canister call blockchain-integridad-backend send_post_request "(\"$POST_URL\", \"$POST_BODY\")")
if [[ "RESPONSE" == *"RESPONSE"* ]]; then
    echo -e "${GREEN}Test passed: send_post_request with valid data${NC}"
else
    echo -e "${RED}Test failed: Expected response to contain 'expected server response' but got $RESPONSE${NC}"
    exit 1
fi

# ----------- SUMMARY -----------

echo -e "${GREEN}All tests passed successfully!${NC}"
