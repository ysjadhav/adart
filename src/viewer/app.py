import os

import streamlit as st

from src.home import select_project, select_task
from src.models.dart_labels import DartLabels
from src.viewer.streamlit_img_label import st_img_label
from src.viewer.streamlit_img_label.image_manager import DartImageDirManager
from src.viewer.streamlit_img_label.manage import ImageManager, ImageDirManager


def run(img_dir, label_dir, labels):
    st.set_option("deprecation.showfileUploaderEncoding", False)
    idm = ImageDirManager(img_dir, label_dir)

    if "img_files" not in st.session_state:
        st.session_state["img_files"] = idm.get_all_img_files()
        st.session_state["annotation_files"] = idm.get_exist_annotation_files()
        st.session_state["image_index"] = 0
        st.session_state["annotation_file_index"] = 0
    else:
        idm.set_all_img_files(st.session_state["img_files"])
        idm.set_annotation_files(st.session_state["annotation_files"])
    
    def refresh():
        st.session_state["img_files"] = idm.get_all_img_files()
        st.session_state["annotation_files"] = idm.get_exist_annotation_files()
        st.session_state["image_index"] = 0
        st.session_state["annotation_file_index"] = 0

    def next_image():
        image_index = st.session_state["image_index"]
        if image_index < len(st.session_state["img_files"]) - 1:
            st.session_state["image_index"] += 1
            st.session_state["annotation_file_index"] += 1
            # print("st.session_state[\"image_index\"] {}".format(st.session_state["image_index"]))
        else:
            st.warning('This is the last image.')

    def previous_image():
        image_index = st.session_state["image_index"]
        if image_index > 0:
            st.session_state["image_index"] -= 1
            st.session_state["annotation_file_index"] -= 1
        else:
            st.warning('This is the first image.')

    def next_annotate_file():
        image_index = st.session_state["image_index"]
        next_image_index = idm.get_next_annotation_image(image_index)
        if next_image_index:
            st.session_state["image_index"] = idm.get_next_annotation_image(image_index)
        else:
            st.warning("All images are annotated.")
            next_image()

    def go_to_image():
        file_index = st.session_state["img_files"].index(st.session_state["img_file"])
        st.session_state["image_index"] = file_index

    # Sidebar: show status
    n_files = len(st.session_state["img_files"])
    n_annotate_files = len(st.session_state["annotation_files"])
    st.sidebar.write("Total files:", n_files)
    st.sidebar.write("Total annotate files:", n_annotate_files)
    st.sidebar.write("Remaining files:", n_files - n_annotate_files)

    st.sidebar.selectbox(
        "Files",
        st.session_state["img_files"],
        index=st.session_state["image_index"],
        on_change=go_to_image,
        key="img_file",
    )
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.button(label="Previous image", on_click=previous_image)
    with col2:
        st.button(label="Next image", on_click=next_image)
    st.sidebar.button(label="Next need annotate", on_click=next_annotate_file)
    st.sidebar.button(label="Refresh", on_click=refresh)

    # Main content: annotate images
    img_file_name = idm.get_image(st.session_state["image_index"])
    annotation_file_name = idm.get_annotation_file(st.session_state["annotation_file_index"])
    img_path = os.path.join(img_dir, img_file_name)
    label_path = os.path.join(label_dir, annotation_file_name)
    im = ImageManager(img_path, label_path)
    img = im.get_img()
    resized_img = im.resizing_img()
    resized_rects = im.get_resized_rects()
    rects = st_img_label(resized_img, box_color="red", rects=resized_rects)

    def annotate():
        im.save_annotation()
        image_annotate_file_name = img_file_name.split(".")[0] + ".xml"
        if image_annotate_file_name not in st.session_state["annotation_files"]:
            st.session_state["annotation_files"].append(image_annotate_file_name)
        print(image_annotate_file_name)
        next_annotate_file()

    if rects:
        st.button(label="Save", on_click=annotate)
        preview_imgs = im.init_annotation(rects)

        for i, prev_img in enumerate(preview_imgs):
            prev_img[0].thumbnail((200, 200))
            col1, col2 = st.columns(2)
            with col1:
                col1.image(prev_img[0])
            with col2:
                default_index = 0
                if prev_img[1]:
                    default_index = labels.index(prev_img[1])

                select_label = col2.selectbox(
                    "Label", labels, key=f"label_{i}", index=default_index
                )
                im.set_annotation(i, select_label)


def main():
    selected_project = select_project()
    if selected_project:
        if not selected_project.label_files:
            st.write("No labels!")
            return

    selected_task = select_task()
    # if selected_task:
    # # TODO:
    # img_dir = None
    # dart_labels = None
    #
    # idm = DartImageDirManager(img_dir, dart_labels)
    #
    # if "img_files" not in st.session_state:
    #     st.session_state["img_files"] = [image.name for image in dart_labels.images]
    #     st.session_state["image_index"] = 0
    # else:
    #     idm.set_all_img_files(st.session_state["img_files"])
    #     idm.set_annotation_files(st.session_state["annotation_files"])
    #
    # def refresh():
    #     st.session_state["img_files"] = idm.get_all_img_files()
    #     st.session_state["annotation_files"] = idm.get_exist_annotation_files()
    #     st.session_state["image_index"] = 0
    #     st.session_state["annotation_file_index"] = 0
    #
    # def next_image():
    #     image_index = st.session_state["image_index"]
    #     if image_index < len(st.session_state["img_files"]) - 1:
    #         st.session_state["image_index"] += 1
    #         st.session_state["annotation_file_index"] += 1
    #         # print("st.session_state[\"image_index\"] {}".format(st.session_state["image_index"]))
    #     else:
    #         st.warning('This is the last image.')
    #
    # def previous_image():
    #     image_index = st.session_state["image_index"]
    #     if image_index > 0:
    #         st.session_state["image_index"] -= 1
    #     else:
    #         st.warning('This is the first image.')
    #
    # def next_annotate_file():
    #     image_index = st.session_state["image_index"]
    #     next_image_index = idm.get_next_annotation_image(image_index)
    #     if next_image_index:
    #         st.session_state["image_index"] = idm.get_next_annotation_image(image_index)
    #     else:
    #         st.warning("All images are annotated.")
    #         next_image()
    #
    # def go_to_image():
    #     file_index = st.session_state["img_files"].index(st.session_state["img_file"])
    #     st.session_state["image_index"] = file_index
    #
    # # Sidebar: show status
    # n_files = len(st.session_state["img_files"])
    # n_annotate_files = len(st.session_state["annotation_files"])
    # st.sidebar.write("Total files:", n_files)
    # st.sidebar.write("Total annotate files:", n_annotate_files)
    # st.sidebar.write("Remaining files:", n_files - n_annotate_files)
    #
    # st.sidebar.selectbox(
    #     "Files",
    #     st.session_state["img_files"],
    #     index=st.session_state["image_index"],
    #     on_change=go_to_image,
    #     key="img_file",
    # )
    # col1, col2 = st.sidebar.columns(2)
    # with col1:
    #     st.button(label="Previous image", on_click=previous_image)
    # with col2:
    #     st.button(label="Next image", on_click=next_image)
    # st.sidebar.button(label="Next need annotate", on_click=next_annotate_file)
    # st.sidebar.button(label="Refresh", on_click=refresh)
    #
    # # Main content: annotate images
    # img_file_name = idm.get_image(st.session_state["image_index"])
    # img_path = os.path.join(img_dir, img_file_name)
    # im = ImageManager(img_path, dart_labels)
    # img = im.get_img()
    # resized_img = im.resizing_img()
    # resized_rects = im.get_resized_rects()
    # rects = st_img_label(resized_img, box_color="red", rects=resized_rects)
    #
    # def annotate():
    #     im.save_annotation()
    #     image_annotate_file_name = img_file_name.split(".")[0] + ".xml"
    #     if image_annotate_file_name not in st.session_state["annotation_files"]:
    #         st.session_state["annotation_files"].append(image_annotate_file_name)
    #     print(image_annotate_file_name)
    #     next_annotate_file()
    #
    # if rects:
    #     st.button(label="Save", on_click=annotate)
    #     preview_imgs = im.init_annotation(rects)
    #
    #     for i, prev_img in enumerate(preview_imgs):
    #         prev_img[0].thumbnail((200, 200))
    #         col1, col2 = st.columns(2)
    #         with col1:
    #             col1.image(prev_img[0])
    #         with col2:
    #             default_index = 0
    #             if prev_img[1]:
    #                 default_index = labels.index(prev_img[1])
    #
    #             select_label = col2.selectbox(
    #                 "Label", labels, key=f"label_{i}", index=default_index
    #             )
    #             im.set_annotation(i, select_label)


if __name__ == "__main__":
    custom_labels = ["", "dog", "cat"]
    run("img_dir", "img_dir", custom_labels)
    # main()
