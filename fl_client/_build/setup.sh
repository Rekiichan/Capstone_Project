#!/bin/bash
source _bash/_config.cfg
source _bash/_functions.sh
source _bash/_flapi_db.sh
source _bash/_flapi_web.sh

# ----------------------------------
# FUNC: Pull git source
# PARAMS: $branch (Git branch)
# ----------------------------------
function pull_source_git() {
    #1. Remove git folder
    rm -rf ${GIT_DIR_PATH}

    #2. Pull source Web App
    show_msg_title "Thực hiện pull source [Web app] from $1 branch"
    git clone --branch $1 ${GIT_URL} ${GIT_DIR_PATH}
}


# ----------------------------------
# FUNC: Clean source git
# PARAMS: None
# ----------------------------------
function clean_source_git() {
    show_msg_title "Thực hiện clean source git"

    rm -rf ${GIT_DIR_PATH}
}

# ----------------------------------
# FUNC: Thực hiện Setup env (local, dev, staging)
# ----------------------------------
function run_action_1_setup_env_on_linux() {
    show_msg_text "------------------------------"
    MAX_STEP="6"

    show_msg_title "[STEP 1/${MAX_STEP}] Pull source git"
    pull_source_git ${GIT_DEVELOP_BRANCH}

    show_msg_title "[STEP 2/${MAX_STEP}] Setup API DB container"
    # flapi_db_setup_env

    show_msg_title "[STEP 3/${MAX_STEP}] Setup API Web container"
    flapi_web_setup_env_linux

    show_msg_title "[STEP ${MAX_STEP}/${MAX_STEP}] Clean source git"
    clean_source_git
}

function run_action_1_setup_env_on_window() {
    show_msg_text "------------------------------"
    MAX_STEP="6"

    show_msg_title "[STEP 1/${MAX_STEP}] Pull source git"
    pull_source_git ${GIT_DEVELOP_BRANCH}

    show_msg_title "[STEP 2/${MAX_STEP}] Setup API DB container"
    flapi_db_setup_env

    show_msg_title "[STEP 3/${MAX_STEP}] Setup API Web container"
    flapi_web_setup_env_window

    show_msg_title "[STEP ${MAX_STEP}/${MAX_STEP}] Clean source git"
    clean_source_git
}


# ----------------------------------
# FUNC: Thực hiện Deployment (local, dev, staging)
# ----------------------------------
function run_action_2_deployment() {
    show_msg_text "------------------------------"
    MAX_STEP="3"

}

# ----------------------------------
# FUNC: Thực hiện Clean docker (local, dev, staging)
# ----------------------------------
function run_action_3_clean_docker() {
    show_msg_text "------------------------------"
}

# ----------------------------------
# FUNC: Thực hiện Backup db
# ----------------------------------
function run_action_1_dump_db() {
    show_msg_text "------------------------------"
    MAX_STEP="3"

    show_msg_title "[STEP 1/${MAX_STEP}] Dump database"
    django-admin dumpdata -o _setup/my_dump.json
    git add .
    git commit -m "Dump database"
}


# ----------------------------------
# FUNC: Thực hiện Push to docker hub
# ----------------------------------
function run_action_1_push_image() {

    show_msg_title "Login to docker hub"
    login_docker

    show_msg_text "------------------------------"
    MAX_STEP="4"
    
    show_msg_title "[STEP 1/${MAX_STEP}] Creare tag for ${DOCKER_API_DB_IMAGE_NAME}"

    read -p "${COLOR_TEXT}Nhập tên tag(version) :" tag_name

    create_image_tag ${DOCKER_API_DB_IMAGE_NAME} ${DOCKER_HUB_REPO_API_DB} ${tag_name}

    show_msg_title "[STEP 2/${MAX_STEP}] Push image  ${DOCKER_API_DB_IMAGE_NAME}"
    push_image_tag ${DOCKER_HUB_REPO_API_DB} ${tag_name}

    show_msg_title "[STEP 3/${MAX_STEP}] Creare tag for  ${DOCKER_API_WEB_IMAGE_NAME}"
    create_image_tag ${DOCKER_API_WEB_IMAGE_NAME} ${DOCKER_HUB_REPO_API_WEB} ${tag_name}

    show_msg_title "[STEP 5/${MAX_STEP}] Push image  ${DOCKER_API_WEB_IMAGE_NAME}"
    push_image_tag ${DOCKER_HUB_REPO_API_WEB} ${tag_name}


}



# ----------------------------------
# FUNC: Hiển thị menu chọn thao tác
# ----------------------------------
function get_action_init() {
    ACTION_1="Setup env on linux"
    ACTION_2="Setup env on window"
    ACTION_3="Deployment"
    ACTION_4="Clean docker"
    ACTION_5="Dump db"
    ACTION_6="Push image to docker hub"

    ACTION_LIST="(1,2,3,4,5,6)"

    show_msg_confirm "Chọn 1 trong các tác vụ sau (Thao tác chỉ được thực hiện trên local): "
    show_msg_text "1. ${ACTION_1}"
    show_msg_text "2. ${ACTION_2}"
    show_msg_text "3. ${ACTION_3}"
    show_msg_text "4. ${ACTION_4}"
    show_msg_text "5. ${ACTION_5}"
    show_msg_text "5. ${ACTION_6}"

    while true; do
    read -p "${COLOR_TEXT}Nhập tác vụ ${ACTION_LIST} :" action
    case $action in
        [1]* ) show_msg_text "Bắt đầu thực hiện ${ACTION_1}"; run_action_1_setup_env_on_linux; break;;
        [2]* ) show_msg_text "Bắt đầu thực hiện ${ACTION_2}"; run_action_1_setup_env_on_window; break;;
        [3]* ) show_msg_text "Bắt đầu thực hiện ${ACTION_3}"; run_action_1_deployment; break;;
        [4]* ) show_msg_text "Bắt đầu thực hiện ${ACTION_4}"; run_action_1_clean_docker; break;;
        [5]* ) show_msg_text "Bắt đầu thực hiện ${ACTION_5}"; run_action_1_dump_db; break;;
        [5]* ) show_msg_text "Bắt đầu thực hiện ${ACTION_6}"; run_action_1_push_image; break;;
        * ) show_msg_error "Vui lòng chọn một trong số tác vụ sau: ${ACTION_LIST}";;
    esac
    done
}

get_action_init