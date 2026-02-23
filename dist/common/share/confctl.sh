#!/bin/bash
set -e

SOURCE=${BASH_SOURCE[0]}
while [ -L "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  TARGET=$(readlink "$SOURCE")
  if [[ $TARGET == /* ]]; then
    SOURCE=$TARGET
  else
    DIR=$( dirname "$SOURCE" )
    SOURCE=$DIR/$TARGET # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
  fi
done

RDIR=$( dirname "$SOURCE" )
DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )
HERE="$DIR"

Help()
{
   echo "confctl.sh - enable / disable patches for cellframe-node configurations."
   echo "Usage: confctl.sh [on | off | list] [ general | network/<netname> ] [patchname]"
   echo "on - enables config patch"
   echo "off - disables config patch"
   echo "list - list available pathes"
   echo "list [general | network/<netname> ] - list enabled patches"
   echo "help - prints this message"
}

containsElement () {
  local e match="$1"
  shift
  for e; do [[ "$e" == "$match" ]] && return 0; done
  return 1
}

COMMANDS=(on off list help)

CMD=$1 #on | off
CFG=$2 #general | network/netname
PATCH=$3 #patch name (with cfg or without)

if [ -z "$CMD" ]
then
	Help
    exit 255
fi

containsElement "$CMD" "${COMMANDS[@]}"  || {
        echo "No such command: $CMD"
        echo 'use "confctl.sh help" for usage'
        exit 255
    }

NODE_PATH=/opt/cellframe-node/
NODE_CFG_PATH=$NODE_PATH/etc/
NODE_CFG_PATH_NET=$NODE_CFG_PATH/network/
NODE_CFG_PATH_GENERAL=$NODE_CFG_PATH/cellframe-node.cfg.d/

NODE_PATCH_PATH=$NODE_PATH/share/configs/patches.d/
NODE_PATCH_PATH_GENERAL=$NODE_PATH/share/configs/patches.d/general/
NODE_PATCH_PATH_NETWORK=$NODE_PATH/share/configs/patches.d/network/


NODE_PATCH_PATH=/opt
if [ "$CMD" == "on" ]
then
    
    if [ -z "$CFG" ]
    then
        echo "No config specified: general | network/<netname>"
        exit 255
    fi

    if [ -z "$PATCH" ]
    then
        echo "No <patchname> specified"
        exit 255
    fi

    #check for CFG validity
    if [ "$CFG" == "general" ]
    then
        #check if patch exists
        if [[ -f "$NODE_PATCH_PATH_GENERAL/$PATCH.cfg" ]]; then
            mkdir -p $NODE_CFG_PATH_GENERAL
            cp "$NODE_PATCH_PATH_GENERAL/$PATCH.cfg" "$NODE_CFG_PATH_GENERAL"
            echo "Enabled [$PATCH] from $NODE_PATCH_PATH_GENERAL in $NODE_CFG_PATH_GENERAL"
            exit 0
        else
            echo "No such config patch: [$PATCH] in $NODE_PATCH_PATH_GENERAL"
            exit 255
        fi
    else
        ARRCFG=(${CFG//// }) 
        if [ ${ARRCFG[0]} == "network" ]
        then
            #check if such network enabled
            
            if [[ -f "$NODE_CFG_PATH_NET/${ARRCFG[1]}.cfg" ]]; then
                if [[ -f "$NODE_PATCH_PATH_NETWORK/$PATCH.cfg" ]]; then
                    mkdir -p $NODE_CFG_PATH_NET/${ARRCFG[1]}.cfg.d/
                    cp "$NODE_PATCH_PATH_NETWORK/$PATCH.cfg" "$NODE_CFG_PATH_NET/${ARRCFG[1]}.cfg.d/"
                    echo "Enabled [$PATCH] from $NODE_PATCH_PATH_NETWORK in $NODE_CFG_PATH_NET/${ARRCFG[1]}.cfg.d/"
                    exit 0
                else
                    echo "No such config patch: [$PATCH] in $NODE_PATCH_PATH_NETWORK"
                    exit 255
                fi
            else
                echo "Network [${ARRCFG[1]}] not active, will not enable patch [$PATCH]"
            fi
            
        else
            echo "No such patch category [${ARRCFG[0]}]"
        fi  
        
    fi
fi

if [ "$CMD" == "off" ]
then
    if [ -z "$CFG" ]
    then
        echo "No config specified: general | network/<netname>"
        exit 255
    fi

    if [ -z "$PATCH" ]
    then
        echo "No <patchname> specified"
        exit 255
    fi

    #check for CFG validity
    if [ "$CFG" == "general" ]
    then
        #check if patch exists
        if [[ -f "$NODE_CFG_PATH_GENERAL/$PATCH.cfg" ]]; then
            
            rm "$NODE_CFG_PATH_GENERAL/$PATCH.cfg"
            echo "Disabled [$PATCH] in $NODE_CFG_PATH_GENERAL"
            exit 0
        else
            echo "No such config patch: $PATCH in $NODE_CFG_PATH_GENERAL"
            exit 255
        fi
    else
        ARRCFG=(${CFG//// }) 
        if [ ${ARRCFG[0]} == "network" ]
        then
            #check if such network enabled
            
            if [[ -f "$NODE_CFG_PATH_NET/${ARRCFG[1]}.cfg" ]]; then
                if [[ -f "$NODE_CFG_PATH_NET/${ARRCFG[1]}.cfg.d/$PATCH.cfg" ]]; then
            
                    rm "$NODE_CFG_PATH_NET/${ARRCFG[1]}.cfg.d/$PATCH.cfg"
                    echo "Disabled [$PATCH] in $NODE_CFG_PATH_NET/${ARRCFG[1]}.cfg.d/"
                    exit 0
                else
                    echo "No such config patch: $PATCH in $NODE_CFG_PATH_NET/${ARRCFG[1]}.cfg.d/"
                    exit 255
                fi
            else
                echo "Network [${ARRCFG[1]}] not active, will not disble patch [$PATCH]"
            fi
            
        else
            echo "No such patch category [${ARRCFG[0]}]"
        fi  
    fi

fi

if [ "$CMD" == "list" ]
then
    if [ -z "$CFG" ]
    then
        echo "General patches:"
        find $NODE_PATCH_PATH_GENERAL/ -name '*.cfg' -exec basename {} .cfg \;
        #for file in $NODE_PATCH_PATH_GENERAL/*; do echo "$(basename ${file%.*})"; done 
        #echo "$(ls  $NODE_PATCH_PATH_GENERAL)"
        echo ""
        echo "Network patches:"
        find $NODE_PATCH_PATH_NETWORK/ -name '*.cfg' -exec basename {} .cfg \;
        exit 0
    fi

    #check for CFG validity
    if [ "$CFG" == "general" ]
    then
        find $NODE_CFG_PATH_GENERAL/ -name '*.cfg' -exec basename {} .cfg \;
    else
        ARRCFG=(${CFG//// }) 
        if [ ${ARRCFG[0]} == "network" ]
        then
            #check if such network enabled
            
            if [[ -f "$NODE_CFG_PATH_NET/${ARRCFG[1]}.cfg" ]]; then
                echo "Enabled patches:"
                find $NODE_CFG_PATH_NET/${ARRCFG[1]}.cfg.d/ -name '*.cfg' -exec basename {} .cfg \;
                exit 0
            
            else
                echo "Network [${ARRCFG[1]}] not active, will not list anything"
            fi
            
        else
            echo "No such patch category [${ARRCFG[0]}]"
        fi  
    fi
  
  exit 0
fi

if [ "$CMD" == "help" ]
then
  Help
  exit 0
fi

