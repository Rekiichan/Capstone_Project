#!/bin/bash

# =======================================================
# FUNC: LOCAL
# =======================================================

# ----------------------------------
# FUNC: Get flapi_web source_code path
# ----------------------------------
function call_flapi_web_get_source_code_path() {
  CURRENT_PATH=$(pwd)
  PARENT_PATH="$(dirname "$CURRENT_PATH")"

  SOURCE_CODE_PATH="${PARENT_PATH}"
}

# ----------------------------------
# FUNC: STEP1: Cleanup
# example: step_1_cleanup
# ----------------------------------
function flapi_web_step_1_cleanup() {
    show_msg_text "[STEP 1/3] Cleanup"

    #1. Xóa docker container
    call_remove_docker_container $DOCKER_API_WEB_CONTAINER_NAME

    #2. Xóa docker image
    call_remove_docker_image $DOCKER_API_WEB_IMAGE_NAME

    #3. Xóa docker volume
    call_remove_docker_volume $DOCKER_API_WEB_VOLUME_NAME

    #3. Check and create Network
    call_check_and_create_network $DOCKER_API_WEB_NET_WORK

    #4. Check and create Volume
    # call_check_and_create_volume $DOCKER_API_WEB_VOLUME_NAME

    show_msg_success "Cleanup thành công."
}

# ----------------------------------
# FUNC: STEP2: Build Image
# example: step_2_build_image
# ----------------------------------
function flapi_web_step_2_build_image() {
  show_msg_text "[STEP 2/3]: Build image"
  call_flapi_web_get_source_code_path

  docker build -f Dockerfile.apiweb.local "${SOURCE_CODE_PATH}" -t ${DOCKER_API_WEB_IMAGE_NAME} --no-cache
  check_exists_docker_image_by_name ${DOCKER_API_WEB_IMAGE_NAME}

  if (($? == 1)); then
    show_msg_success "Build $DOCKER_API_WEB_IMAGE_NAME image thành công."
  else
    show_msg_error "Build $DOCKER_API_WEB_IMAGE_NAME image thất bại. Vui lòng kiểm tra lại trên Docker."
  fi

}

# ----------------------------------
# FUNC: STEP2: Pull Image
# example: step_2_pull_image
# ----------------------------------
function flapi_web_step_2_pull_image() {
  show_msg_text "[STEP 2/3]: Pull image"

  # Login docker
  login_docker

  # Pull image
  pull_docker_image ${DOCKER_API_WEB_IMAGE_NAME} ${DOCKER_HUB_REPO_API_WEB}:$1
  
  check_exists_docker_image_by_name ${DOCKER_API_WEB_IMAGE_NAME}

  if (($? == 1)); then
    show_msg_success "Pull $DOCKER_API_WEB_IMAGE_NAME image thành công."
  else
    show_msg_error "Pull $DOCKER_API_WEB_IMAGE_NAME image thất bại. Vui lòng kiểm tra lại trên Docker."
  fi

}

# ----------------------------------
# FUNC: STEP3: Create container on linux
# example: step_3_create_container on linux
# ----------------------------------
function flapi_web_step_3_create_container_linux() {
  show_msg_text "[STEP 3/3]: Create Container"

  check_exists_docker_image_by_name ${DOCKER_API_WEB_IMAGE_NAME}

  if (($? == 1)); then
    #1. Kiểm tra các thành phần đi kèm
    #1.1 Docker network
    check_exists_docker_network_by_name $DOCKER_API_WEB_NET_WORK
    if (($? == 0)); then
      show_msg_text "Không tìm thấy $DOCKER_API_WEB_NET_WORK network. Đang thực hiện tạo $DOCKER_API_WEB_NET_WORK network ..."
      create_docker_network ${DOCKER_API_WEB_NET_WORK}
    fi

    #1.2 Docker volume
    COUNT=$(docker volume ls | grep "$DOCKER_API_WEB_VOLUME_NAME" | wc -l)
    if (($COUNT == 0)); then
      show_msg_text "Không tìm thấy $DOCKER_API_WEB_VOLUME_NAME volume. Đang thực hiện tạo $DOCKER_API_WEB_VOLUME_NAME volume ..."
      create_docker_volume $DOCKER_API_WEB_VOLUME_NAME
    fi

    #2. Tạo akpapi_web container
    #2.1 Tạo mới akpapi_web container
    call_flapi_web_get_source_code_path
    echo "docker run -ti --name ${DOCKER_API_WEB_CONTAINER_NAME} --net=${DOCKER_API_DB_NET_WORK} --hostname=${DOCKER_API_WEB_HOST} -d -v ${DOCKER_API_WEB_VOLUME_NAME}:/${DOCKER_API_WEB_VOLUME_NAME} -v "${SOURCE_CODE_PATH}/source_code":/fl -p ${DOCKER_API_WEB_HOST_PORT}:${DOCKER_API_WEB_MACHINE_PORT} ${DOCKER_API_WEB_IMAGE_NAME}:${DOCKER_API_WEB_IMAGE_VERSION}"
    docker run -ti --name ${DOCKER_API_WEB_CONTAINER_NAME} --net=${DOCKER_API_DB_NET_WORK} --hostname=${DOCKER_API_WEB_HOST} -d -v ${DOCKER_API_WEB_VOLUME_NAME}:/${DOCKER_API_WEB_VOLUME_NAME} -v "${SOURCE_CODE_PATH}/source_code":/fl -p ${DOCKER_API_WEB_HOST_PORT}:${DOCKER_API_WEB_MACHINE_PORT} ${DOCKER_API_WEB_IMAGE_NAME}:${DOCKER_API_WEB_IMAGE_VERSION}

    #2.2 Kiểm tra kết quả
    check_exists_docker_container_by_name $DOCKER_API_WEB_CONTAINER_NAME
    if (($? == 1)); then
      show_msg_success "Tạo $DOCKER_API_WEB_CONTAINER_NAME container thành công."
    fi
  else
    show_msg_error "Không tìm thấy ${DOCKER_API_WEB_IMAGE_NAME} image -> Vui lòng kiểm tra lại trên Docker ... "
  fi
}

# ----------------------------------
# FUNC: STEP3: Create container on window
# example: step_3_create_container on window
# ----------------------------------
function flapi_web_step_3_create_container_window() {
  show_msg_text "[STEP 3/3]: Create Container"

  check_exists_docker_image_by_name ${DOCKER_API_WEB_IMAGE_NAME}

  if (($? == 1)); then
    #1. Kiểm tra các thành phần đi kèm
    #1.1 Docker network
    check_exists_docker_network_by_name $DOCKER_API_WEB_NET_WORK
    if (($? == 0)); then
      show_msg_text "Không tìm thấy $DOCKER_API_WEB_NET_WORK network. Đang thực hiện tạo $DOCKER_API_WEB_NET_WORK network ..."
      create_docker_network ${DOCKER_API_WEB_NET_WORK}
    fi

    #1.2 Docker volume
    COUNT=$(docker volume ls | grep "$DOCKER_API_WEB_VOLUME_NAME" | wc -l)
    if (($COUNT == 0)); then
      show_msg_text "Không tìm thấy $DOCKER_API_WEB_VOLUME_NAME volume. Đang thực hiện tạo $DOCKER_API_WEB_VOLUME_NAME volume ..."
      create_docker_volume $DOCKER_API_WEB_VOLUME_NAME
    fi

    #2. Tạo akpapi_web container
    #2.1 Tạo mới akpapi_web container
    # call_flapi_web_get_source_code_path

    docker run -ti --restart always --name ${DOCKER_API_WEB_CONTAINER_NAME} --net=${DOCKER_API_DB_NET_WORK} --hostname=${DOCKER_API_WEB_HOST} -d -v ${DOCKER_API_WEB_VOLUME_NAME}:/${DOCKER_API_WEB_VOLUME_NAME} -v "${DOCKER_VOLUME_PATH_WINDOW}":/fl -p ${DOCKER_API_WEB_HOST_PORT}:${DOCKER_API_WEB_MACHINE_PORT} ${DOCKER_API_WEB_IMAGE_NAME}:${DOCKER_API_WEB_IMAGE_VERSION}
    echo ${DOCKER_API_WEB_VOLUME_NAME}
    #2.2 Kiểm tra kết quả
    check_exists_docker_container_by_name $DOCKER_API_WEB_CONTAINER_NAME
    if (($? == 1)); then
      show_msg_success "Tạo $DOCKER_API_WEB_CONTAINER_NAME container thành công."
    fi
  else
    show_msg_error "Không tìm thấy ${DOCKER_API_WEB_IMAGE_NAME} image -> Vui lòng kiểm tra lại trên Docker ... "
  fi
}

# ----------------------------------
# FUNC: Export db
# ----------------------------------
function flapi_web_dump_db() {
  check_exists_docker_container_active_by_name ${DOCKER_API_WEB_CONTAINER_NAME}
  if (($? == 1)); then
    #1. Get ngày hiện tại
    CURRENT_DATE=$(date +'%Y-%m-%d')
    IN_PATH_DEFAULT="flapi_db_${CURRENT_DATE}.json.gz"

    read -p "Nhập tên file SQL [$IN_PATH_DEFAULT] :" SQL_FILE_NAME_INPUT

    SQL_FILE_NAME_INPUT="${SQL_FILE_NAME_INPUT:-$IN_PATH_DEFAULT}"

    #2. Dump SQL File vào container
    docker exec -it ${DOCKER_API_WEB_CONTAINER_NAME} python manage.py dumpdata --indent 2 -o /backup_db/${SQL_FILE_NAME_INPUT}

    #3. Copy from Container to Host
    docker cp ${DOCKER_API_WEB_CONTAINER_NAME}:/${DOCKER_API_BACKUP_VOLUME_NAME}/${SQL_FILE_NAME_INPUT} ${API_DB_HOST_SQL_DUMP_PATH}/
    check_exist_file $API_DB_HOST_SQL_DUMP_PATH $SQL_FILE_NAME_INPUT

    if (($? == 1)); then
      echo "${COLOR_TEXT}---> Export Database ${SQL_FILE_NAME_INPUT} thành công."
    fi
  else
    echo "${COLOR_MSG} ---> $1 container chưa được chạy. Vui lòng kiểm tra lại trên Docker ... ${COLOR_TEXT}"
  fi
}

# ----------------------------------
# FUNC: Setup
# ----------------------------------
# FOR LINUX OS
function flapi_web_setup_env_linux() {
  flapi_web_step_1_cleanup
  flapi_web_step_2_build_image
  flapi_web_step_3_create_container_linux
}

# FOR WINDOW OS
function flapi_web_setup_env_window() {
  flapi_web_step_1_cleanup
  flapi_web_step_2_build_image
  flapi_web_step_3_create_container_window
}

function flapi_web_setup_env_via_docker_hub() {
  flapi_web_step_1_cleanup
  flapi_web_step_2_pull_image $1
  flapi_web_step_3_create_container_linux
}
