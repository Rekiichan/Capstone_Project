#!/bin/bash

# ----------------------------------
# FUNC: Show message info
# PARAMS: $MSG (Message)
# ----------------------------------
function show_msg_title() {
  echo "${COLOR_TITLE}$1${COLOR_TEXT}"
}

# ----------------------------------
# FUNC: Show message success
# PARAMS: $MSG (Message)
# ----------------------------------
function show_msg_success() {
  echo "→ ${COLOR_SUCCESS}$1${COLOR_TEXT}"
}

# ----------------------------------
# FUNC: Show message success
# PARAMS: $MSG (Message)
# ----------------------------------
function show_msg_error() {
  echo "→ ${COLOR_ERROR}$1${COLOR_TEXT}"
}

# ----------------------------------
# FUNC: Show message confirm
# PARAMS: $MSG (Message)
# ----------------------------------
function show_msg_confirm() {
  echo "→ ${COLOR_CONFIRM}$1${COLOR_TEXT}"
}

# ----------------------------------
# FUNC: Show message text
# PARAMS: $MSG (Message)
# ----------------------------------
function show_msg_text() {
  echo "${COLOR_TEXT}$1${COLOR_TEXT}"
}

# ----------------------------------
# FUNC: Tạo 1 Docker network 
# PARAMS: $NETWORK_NAME (Tên network)
# ----------------------------------
function create_docker_network() {
  docker network create -d bridge $1
  check_exists_docker_network_by_name $1

  if (($? == 1)); then
    show_msg_success "Tạo $1 network thành công."
  else
    show_msg_error "Tạo $1 network thất bại. Vui lòng kiểm tra lại trên Docker machine."
  fi
}

# ----------------------------------
# Tạo 1 Docker volume 
# example: create_docker_volume $VOLUME_NAME
# ----------------------------------
function create_docker_volume() {
  docker volume create $1

  COUNT=$(docker volume ls | grep "$1" | wc -l)

  if (($COUNT == 1)); then
    show_msg_success "Tạo $1 volume thành công."
  else
    show_msg_error "Tạo $1 volume thất bại. Vui lòng kiểm tra lại trên Docker machine."
  fi
}

# ----------------------------------
# FUNC: Kiểm tra tồn tại file trong đường dẫn
# ----------------------------------
function check_exist_file() {
  COUNT=$(ls $1 | grep "$2" | wc -l)
  if (($COUNT > 0)); then
    return 1
  else
    return 0
  fi
}

# ----------------------------------
# FUNC: Check tồn tại Docker container đang chạy với Docker Machine Port
# PARAMS: $MACHINE_PỎT (PORT đang chạy trên Docker Machine)
# ----------------------------------
function check_exists_docker_container_active_in_expose() {
  COUNT=$(docker ps --filter expose=$1 --format {{.Names}} | wc -l)
  if (($COUNT > 0)); then
    confirm_stop_docker_container_active_in_expose
    return 1
  else
    return 0
  fi
}

# ----------------------------------
# FUNC: Check tồn tại Docker container đang chạy với HOST Port
# PARAMS: $PUBLISH_PORT (PORT đang publish ra Host)
# ----------------------------------
function check_exists_docker_container_active_in_publish() {
  COUNT=$(docker ps --filter publish=$1 --format {{.Names}} | wc -l)
  if (($COUNT > 0)); then
    confirm_stop_docker_container_active_in_publish
    return 1
  else
    return 0
  fi
}

# ----------------------------------
# FUNC: Get tên Docker container đang chạy với Publish Port
# PARAMS: $PUBLISH_PORT (PORT đang chạy publish ra HOST)
# ----------------------------------
function get_docker_container_active_in_publish() {
  CONTAINER_NAME=$(docker ps --filter publish=$1 --format {{.Names}})
  return $CONTAINER_NAME
}

# ----------------------------------
# FUNC: Get tên Docker container đang chạy với Docker Port
# PARAMS: $EXPOSE_PORT (PORT đang chạy trên Docker)
# ----------------------------------
function get_docker_container_active_in_expose() {
  CONTAINER_NAME=$(docker ps --filter expose=$1 --format {{.Names}})
  return $CONTAINER_NAME
}

# ----------------------------------
# FUNC: Check tồn tại Docker network by name
# PARAMS: $NETWORK_NAME (Tên network)
# ----------------------------------
function check_exists_docker_network_by_name() {
  COUNT=$(docker network ls | grep "$1" | wc -l)
  if (($COUNT > 0)); then
    return 1
  else
    return 0
  fi
}

# ----------------------------------
# FUNC: Check tồn tại Docker volume by name
# PARAMS: $VOL_NAME (Tên volume)
# ----------------------------------
function check_exists_docker_volume_by_name() {
  COUNT=$(docker volume ls | grep "$1" | wc -l)
  if (($COUNT > 0)); then
    return 1
  else
    return 0
  fi
}

# ----------------------------------
# FUNC: Check tồn tại Docker container by name
# PARAMS: $COTAINER_NAME (Tên container)
# ----------------------------------
function check_exists_docker_container_by_name() {
  COUNT=$(docker ps -a | grep "$1" | wc -l)
  if (($COUNT > 0)); then
    return 1
  else
    return 0
  fi
}

# ----------------------------------
# FUNC: Check tồn tại Docker container (active) by name
# PARAMS: $COTAINER_NAME (Tên container)
# ----------------------------------
function check_exists_docker_container_active_by_name() {
  COUNT=$(docker ps | grep "$1" | wc -l)
  if (($COUNT > 0)); then
    return 1
  else
    return 0
  fi
}

# ----------------------------------
# FUNC: Check tồn tại Docker image by name + version
# PARAMS: $IMAGE_NAME (Tên image), $IMAGE_VERSION (Version)
# ----------------------------------
function check_exists_docker_image_by_name_and_version() {
  COUNT=$(docker images --format="{{.Repository}}:{{.Tag}}" | grep "$1:$2" | wc -l)
  if (($COUNT > 0)); then
    return 1
  else
    return 0
  fi
}

# ----------------------------------
# FUNC: Check tồn tại Docker image by name
# PARAMS: $IMAGE_NAME (Tên image)
# ----------------------------------
function check_exists_docker_image_by_name() {
  COUNT=$(docker images --format="{{.Repository}}:{{.Tag}}" | grep "$1" | wc -l)
  if (($COUNT > 0)); then
    return 1
  else
    return 0
  fi
}

# ----------------------------------
# FUNC: Check tồn tại Docker volume by name
# PARAMS: $VOLUME_NAME (Tên volume)
# ----------------------------------
function check_exists_docker_volume_by_name() {
  COUNT=$(docker volume ls --format="{{.Repository}}:{{.Tag}}" | grep "$1" | wc -l)
  if (($COUNT > 0)); then
    return 1
  else
    return 0
  fi
}

# ----------------------------------
# FUNC: Remove image by name
# PARAMS: $IMAGE_NAME (Tên image)
# ----------------------------------
function remove_docker_image() {
  docker rmi $1
  check_exists_docker_image_by_name $1

  if (($? == 0)); then
    show_msg_success "Xóa $1 image thành công."
  else
    show_msg_error "Xóa $1 image thất bại. Vui lòng kiểm tra lại trên Docker."
  fi
}

# ----------------------------------
# FUNC: Restart container
# PARAMS: $C_NAME (Tên container)
# ----------------------------------
function restart_docker_container() {
  docker restart $1
  check_exists_docker_container_active_by_name $1

  if (($? == 0)); then
    show_msg_success "Khởi động $1 container thành công."
  else
    show_msg_error "Khởi động $1 container thất bại. Vui lòng kiểm tra lại trên Docker."
  fi
}

# ----------------------------------
# FUNC: Remove container by name
# PARAMS: $C_NAME (Tên container)
# ----------------------------------
function remove_docker_container() {
  docker stop $1
  docker rm $1
  check_exists_docker_container_by_name $1

  if (($? == 0)); then
    show_msg_success "Xóa $1 container thành công."
  else
    show_msg_error "Xóa $1 container thất bại. Vui lòng kiểm tra lại trên Docker."
  fi
}

# ----------------------------------
# FUNC: STOP container by name
# PARAMS: $C_NAME (Tên container)
# ----------------------------------
function stop_docker_container() {
  docker stop $1
  check_exists_docker_container_by_name $1

  if (($? == 0)); then
    show_msg_success "Xóa $1 container thành công."
  else
    show_msg_error "Xóa $1 container thất bại. Vui lòng kiểm tra lại trên Docker."
  fi
}

# ----------------------------------
# FUNC: STOP container by name
# PARAMS: $C_NAME (Tên container)
# ----------------------------------
function remove_docker_volume() {
  docker volume rm $1

  COUNT=$(docker volume ls | grep "$1" | wc -l)

  if (($COUNT == 0)); then
    show_msg_success "Xóa $1 volume thành công."
  else
    show_msg_error "Xóa $1 volume thất bại. Vui lòng kiểm tra lại trên Docker machine."
  fi
}

# ----------------------------------
# FUNC: Xác nhận STOP container đang chạy tại Docker Port
# PARAMS: $EXPOSE_PORT (Port đang chạy tại Docker)
# ----------------------------------
function confirm_stop_docker_container_active_in_expose() {
  get_docker_container_active_in_expose $1
  show_msg_confirm "Tồn tại $? container đang chạy trên Docker PORT $1. Bạn có muốn stop $? container ?"
  while true; do
    read -p "${COLOR_TEXT} Nhập y hoặc n (default>y) : ${COLOR_TEXT}" action
    if [ "$action" == "" ]; then
      show_msg_text "Thực hiện STOP $? container ..."
      break;
    else
      case $action in
          [Yy]* ) show_msg_text "Thực hiện STOP $? container ..."; stop_docker_container; break;;
          [Nn]* ) show_msg_text "Bỏ qua STOP container ${DOCKER_API_DB_CONTAINER_NAME}"; break;;
          * ) show_msg_text "Vui lòng chọn một trong các ký tự sau (y,n)";;
      esac
    fi
  done
}

# ----------------------------------
# FUNC: Xác nhận STOP container đang chạy tại Host Port
# PARAMS: $PUBLISH_PORT (Port đang chạy tại Host)
# ----------------------------------
function confirm_stop_docker_container_active_in_publish() {
  get_docker_container_active_in_publish $1
  show_msg_confirm "Tồn tại $? container đang chạy trên Host PORT $1. Bạn có muốn stop $? container ?"
  while true; do
    read -p "${COLOR_TEXT} Nhập y hoặc n (default>y) : ${COLOR_TEXT}" action
    if [ "$action" == "" ]; then
      show_msg_text "Thực hiện STOP $? container ...";  stop_docker_container
      break;
    else
      case $action in
          [Yy]* ) show_msg_text "Thực hiện STOP $? container ..."; stop_docker_container; break;;
          [Nn]* ) show_msg_text "Bỏ qua STOP container ${DOCKER_API_DB_CONTAINER_NAME}"; break;;
          * ) show_msg_text "Vui lòng chọn một trong các ký tự sau (y,n)";;
      esac
    fi
  done
}

# ----------------------------------
# FUNC: Remove container
# PARAMS: $CONTAINER_NAME
# ----------------------------------
function call_remove_docker_container() {
  show_msg_text "Xóa $1 container"
  check_exists_docker_container_by_name $1
  if (($? == 1)); then
    show_msg_text "Tìm thấy $1 container -> Đang thực hiện xóa $1 container ..."
    remove_docker_container $1
  else
    show_msg_text "Không tìm thấy $1 container -> Chuyển qua bước tiếp theo ..."
  fi
}

# ----------------------------------
# FUNC: Remove image
# PARAMS: $IMAGE_NAME
# ----------------------------------
function call_remove_docker_image() {
  show_msg_text "Xóa $1 image"
  check_exists_docker_image_by_name $1
  if (($? == 1)); then
    show_msg_text "Tìm thấy $1 image -> Đang thực hiện xóa $1 image ..."
    remove_docker_image $1
  else
    show_msg_text "Không tìm thấy $1 image -> Chuyển qua bước tiếp theo ..."
  fi
}

# ----------------------------------
# FUNC: Remove volume
# PARAMS: $VOLUME_NAME
# ----------------------------------
function call_remove_docker_volume() {
  show_msg_text "Xóa $1 volume"

  COUNT=$(docker volume ls | grep "$1" | wc -l)
  
  if (($COUNT == 1)); then
    show_msg_text "Tìm thấy $1 volume -> Đang thực hiện xóa $1 volume ..."
    remove_docker_volume $1
  else
    show_msg_text "Không tìm thấy $1 volume -> Chuyển qua bước tiếp theo ..."
  fi
}

# ----------------------------------
# FUNC: Check and create Network
# PARAMS: $NETWORK_NAME
# ----------------------------------
function call_check_and_create_network() {
  show_msg_text "Check and create $1 network"
  check_exists_docker_network_by_name $1
  if (($? == 0)); then
    show_msg_text "Không tìm thấy $1 network -> Tạo mới $1 network ..."
    create_docker_network $1
  else
    show_msg_text "Tìm thấy $1 network -> Chuyển qua bước tiếp theo ..."
  fi
}

# ----------------------------------
# FUNC: Remove network
# PARAMS: $IMAGE_NAME
# ----------------------------------
function call_remove_docker_network() {
  show_msg_text "Xóa $1 network"
  check_exists_docker_network_by_name $1
  if (($? == 1)); then
    show_msg_text "Tìm thấy $1 network -> Đang thực hiện xóa $1 network ..."
    remove_docker_network $1
  else
    show_msg_text "Không tìm thấy $1 etwork -> Chuyển qua bước tiếp theo ..."
  fi
}

# ----------------------------------
# FUNC: STOP container by name
# PARAMS: $C_NAME (Tên container)
# ----------------------------------
function remove_docker_network() {
  docker network rm $1
  check_exists_docker_network_by_name $1

  if (($? == 0)); then
    show_msg_text "Xóa $1 network thành công."
  else
    show_msg_text "Xóa $1 network thất bại. Vui lòng kiểm tra lại trên Docker ..."
  fi
}


# ----------------------------------
# FUNC: Check and create Network
# PARAMS: $NETWORK_NAME
# ----------------------------------
function call_check_and_create_volume() {
  show_msg_text "Check and create $1 volume"
  check_exists_docker_volume_by_name $1
  if (($? == 0)); then
    show_msg_text "Không tìm thấy $1 volume -> Tạo mới $1 volume"
    create_docker_volume $1
  fi
}

# ----------------------------------
# FUNC: login docker
# ----------------------------------
function login_docker() {
  docker logout

  docker login --username=$DOCKER_HUB_USERNAME --password=$DOCKER_HUB_PASSWORD
}

function pull_docker_image() {
  # $1 : container name in local
  # $2 : docker hub image

  docker pull $2 
  docker tag $2 $1

  check_exists_docker_image_by_name $1

  if (($? == 1)); then
    show_msg_success "Pull image for $1 thành công."
  else
    show_msg_error "Pull image $1 thất bại. Vui lòng kiểm tra lại trên Docker."
  fi

}


# ----------------------------------
# FUNC: create image tag
# ----------------------------------
function create_image_tag() {
  # $1 : container name in local
  # $2 : docker hub repo
  # $3 : version name

  show_msg_success "Create tag $1 for $2:$3 -----."


  docker tag $1 $2:$3

  check_exists_docker_image_by_name $2 $3

  if (($? == 1)); then
    show_msg_success "Create tag for $1 thành công."
  else
    show_msg_error "Create tag $1 thất bại. Vui lòng kiểm tra lại trên Docker."
  fi

}

function push_image_tag() {
  # $1 : container name in local
  # $2 : docker hub repo
  
  show_msg_success "Push $1:$2 -----."

  docker push $1:$2

  show_msg_success "Push $1:$2 done -----."


}
