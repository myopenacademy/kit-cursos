#!/bin/bash
# Cuenta los clientes de una ciudad en clientes.json (un cliente por línea)
ciudad="$1"
total=$(grep -c "\"ciudad\": \"$ciudad\"" clientes.json)
echo "Clientes de $ciudad: $total"
