#!/bin/bash

PYTHON_EXECUTABLE=py # Windows Python Launcher by default

if [ "$#" -eq "1" ]; then
    PYTHON_EXECUTABLE=$1 # custom python executable
fi

# dependencies
RAPIDJSON="../external/rapidjson/include"

CC=g++
CFLAGS="-std=c++17 -Wall -Werror -Wextra -pedantic -I$RAPIDJSON"
VERBOSE=1

log() {
    if (( $VERBOSE == 1 )); then
        echo " --info: $1"    
    fi
}

compiled=0

# create directory if not exist
[[ -d cpp ]] || mkdir cpp

for input in $(ls ./res); do
    if [[ -f "res/$input" ]] && [[ "$input" == *.json ]]; then
        src="${input%%.json}.cpp"
        obj="${input%%.json}.o"
        
        log "generate $src"
        $PYTHON_EXECUTABLE gen.py -i "res/$input" -o "cpp/$src"
        
        log "compile $src..."
        cd cpp && $CC $CFLAGS -c "$src"
        code=$?
        cd ..

        if [[ $code -eq "0" ]] && [[ -f "cpp/$obj" ]]; then
            log "$obj is compiled"
            compiled=$((compiled + 1))
        else
            log "$obj is not compiled"
            exit 1
        fi
    fi
done

# cleanup
[[ -d cpp ]] && rm -r cpp

log "---------------------------------"
log "Summary: compiled $compiled files"
