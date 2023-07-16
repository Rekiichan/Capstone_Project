#!/bin/bash

# =======================================================
# FUNC: LOCAL
# =======================================================

# ----------------------------------
# FUNC: STEP1: Cleanup
# example: step_1_cleanup
# ----------------------------------
function flapi_db_step_1_cleanup() {
    show_msg_text "[STEP 1/3] Cleanup"

    #1. Xóa docker container
    call_remove_docker_container $DOCKER_API_DB_CONTAINER_NAME

    #2. Xóa docker image
    call_remove_docker_image $DOCKER_API_DB_IMAGE_NAME

    #3. Xóa docker volume
    call_remove_docker_volume $DOCKER_API_DB_VOLUME_NAME

    #4. Check and create Network
    #call_check_and_create_network $DOCKER_API_DB_NET_WORK

    #5. Check and create Volume
    #call_check_and_create_volume $DOCKER_API_DB_VOLUME_NAME

    show_msg_success "Cleanup thành công."
}

# ----------------------------------
# FUNC: STEP2: Build Image
# example: step_2_build_image
# ----------------------------------
function flapi_db_step_2_build_image() {
  show_msg_text "[STEP 2/3]: Build image"
  call_flapi_web_get_source_code_path
  docker build -f Dockerfile.apidb.local ${SOURCE_CODE_PATH} -t c9vioet/${DOCKER_API_DB_IMAGE_NAME} --no-cache
  check_exists_docker_image_by_name ${DOCKER_API_DB_IMAGE_NAME}

  if (($? == 1)); then
    show_msg_success "Build $DOCKER_API_DB_IMAGE_NAME image thành công."
  else
    show_msg_error "Build $DOCKER_API_DB_IMAGE_NAME image thất bại. Vui lòng kiểm tra lại trên Docker."
  fi

}


# ----------------------------------
# FUNC: STEP2: Pull Image
# example: step_2_pull_image
# ----------------------------------
function flapi_db_step_2_pull_image() {
  show_msg_text "[STEP 2/3]: Pull image"

  # Login docker
  login_docker

  # Login docker
  pull_docker_image ${DOCKER_API_DB_IMAGE_NAME} ${DOCKER_HUB_REPO_API_DB}:$1
  
  check_exists_docker_image_by_name ${DOCKER_API_DB_IMAGE_NAME}

  if (($? == 1)); then
    show_msg_success "Pull $DOCKER_API_DB_IMAGE_NAME image thành công."
  else
    show_msg_error "Pull $DOCKER_API_DB_IMAGE_NAME image thất bại. Vui lòng kiểm tra lại trên Docker."
  fi

}


# ----------------------------------
# FUNC: STEP3: Create container
# example: step_3_create_container
# ----------------------------------
function flapi_db_step_3_create_container() {
  show_msg_text "[STEP 3/3]: Create Container"

  check_exists_docker_image_by_name $DOCKER_API_DB_IMAGE_NAME

  if (($? == 1)); then
    #1. Kiểm tra các thành phần đi kèm
    #1.1 Docker network
    check_exists_docker_network_by_name $DOCKER_API_DB_NET_WORK
    if (($? == 0)); then
      show_msg_text "Không tìm thấy $DOCKER_API_DB_NET_WORK network. Đang thực hiện tạo $DOCKER_API_DB_NET_WORK network ..."
      create_docker_network $DOCKER_API_DB_NET_WORK
    fi

    #1.2 Docker volume
    COUNT=$(docker volume ls | grep "$DOCKER_API_DB_VOLUME_NAME" | wc -l)
    if (($COUNT == 0)); then
      show_msg_text "Không tìm thấy $DOCKER_API_DB_VOLUME_NAME volume. Đang thực hiện tạo $DOCKER_API_DB_VOLUME_NAME volume ..."
      create_docker_volume $DOCKER_API_DB_VOLUME_NAME
    fi

    #2. Tạo growme_db container
    #2.1 Tạo mới growme_db container
    docker run -d -ti --name ${DOCKER_API_DB_CONTAINER_NAME} --net=${DOCKER_API_DB_NET_WORK} --hostname=${DOCKER_API_DB_HOST} -d -v ${DOCKER_API_DB_VOLUME_NAME}:/var/lib/mysql -p ${DOCKER_API_DB_HOST_PORT}:${DOCKER_API_DB_MACHINE_PORT} ${DOCKER_API_DB_IMAGE_NAME}:${DOCKER_API_DB_IMAGE_VERSION} --character-set-server=utf8 --collation-server=utf8_unicode_ci
    echo "docker run -d -ti --name ${DOCKER_API_DB_CONTAINER_NAME} --net=${DOCKER_API_DB_NET_WORK} --hostname=${DOCKER_API_DB_HOST} -d -v ${DOCKER_API_DB_VOLUME_NAME}:/var/lib/mysql -p ${DOCKER_API_DB_HOST_PORT}:${DOCKER_API_DB_MACHINE_PORT} ${DOCKER_API_DB_IMAGE_NAME}:${DOCKER_API_DB_IMAGE_VERSION} --character-set-server=utf8 --collation-server=utf8_unicode_ci"

    #2.2 Kiểm tra kết quả
    check_exists_docker_container_by_name $DOCKER_API_DB_CONTAINER_NAME
    if (($? == 1)); then
      show_msg_success "Tạo $DOCKER_API_DB_CONTAINER_NAME container thành công."
    fi
  else
    show_msg_error "Không tìm thấy ${DOCKER_API_DB_CONTAINER_NAME} image -> Vui lòng kiểm tra lại trên Docker ... "
  fi
}

# ----------------------------------
# FUNC: Setup
# ----------------------------------
function flapi_db_setup_env() {
  flapi_db_step_1_cleanup
  flapi_db_step_2_build_image
  flapi_db_step_3_create_container
}

function flapi_db_setup_env_via_docker_hub() {
  flapi_db_step_1_cleanup
  flapi_db_step_2_pull_image $1
  flapi_db_step_3_create_container
}

