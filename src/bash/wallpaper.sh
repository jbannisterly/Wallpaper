#!/bin/bash

args=("$@")

animate=true
lowpower=false

for arg in "${args[@]}"; do
    case "${arg}" in
        --noanimate)
            animate=false
        ;;
        --lowpower)
            lowpower=true
            animate=false
            echo "lowpower"
        ;;
    esac
done

if [ -f ./temp/lowpower ]; then
    rm ./temp/lowpower
fi

if [ -f ./temp/noanimate ]; then
    rm ./temp/noanimate
fi

if [ -f ./temp/nogenerate ]; then
    rm ./temp/nogenerate
fi

if [ "$lowpower" = true ]; then
    touch ./temp/lowpower
fi

if [ "$animate" = false ]; then
    touch ./temp/noanimate
fi

source ./venv/bin/activate
bash ./src/bash/animate.sh &
bash ./src/bash/generate.sh &
