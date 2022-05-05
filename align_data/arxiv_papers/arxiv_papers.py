import os
import re
import csv
import json
from time import sleep
import jsonlines
import chardet
import pandas as pd
import pickle
import magic

mime = magic.Magic(mime=True)
from tqdm import tqdm
import traceback
from pathlib import Path
import multiprocessing as mp
import argparse
from align_data.common.utils import *
import arxiv
import wget


class ArxivPapers:
    def __init__(self, papers_csv_path="data/raw/csvs/ai-alignment-papers.csv"):
        self.papers_csv_path = papers_csv_path
        self.name = "arxiv.org"

    def fetch_entries(self):
        """
        Fetch all the arxiv entries from the arxiv API.
        """
        ## TODO: Add argparse to make this easier to use and rerun
        print("Setting up directory structure...")
        self.setup()
        dl_papers_answer = input("Download papers? (y/n): ")
        if dl_papers_answer == "y":
            print("Downloading all source files for arxiv entries...")
            self.arxiv_dict = self.download_arxiv_papers()
        if ls("files") == []:
            sh(f"mv {self.TARS_DIR}/* files/")
        print("Extracting text and citations from arxiv entries...")
        self.automatic_mode_done = False
        if self.automatic_mode == "y":
            self.automatic_extraction()
            sh(
                f"rm -rf tmp && mkdir tmp"
            )  # should be empty but just in case it has .DS_Store files
        self.automatic_mode_done = True
        if self.manual_mode == "y":
            self.manual_extraction()

        self._mv_empty_mds()
        print("Done extracting text and citations from arxiv entries.")

        print("Finished converting all papers.")
        print("Updating arxiv_dict.json...")
        # loop through files in out/ and outtxt/ and add to arxiv_dict
        for i, mdfile in enumerate(tqdm(ls("out"))):
            print(f"{i}/{len(ls('out'))}")
            self.insert_text_in_dict(mdfile)

        for i, main_tex_name_txt in enumerate(tqdm(ls("outtxt"))):
            print(f"{i}/{len(ls('outtxt'))}")
            self.insert_main_tex_in_dict(main_tex_name_txt)

        if self.remove_empty_papers == "y":
            self.arxiv_dict = self._remove_empty_mds_from_dict()
            self.arxiv_dict = self._remove_empty_texts_from_dict()
        json.dump(
            self.arxiv_dict, open(f"{self.PROCESSED_JSONS_DIR}/arxiv_dict.json", "w")
        )
        print("Finished updating arxiv_dict.json.")

        self.arxiv_list_of_dicts = []
        for paper_id in tqdm(self.arxiv_dict.keys()):
            self.arxiv_list_of_dicts.append(self.arxiv_dict[paper_id])
        json.dump(
            self.arxiv_list_of_dicts,
            open(f"{self.PROCESSED_JSONS_DIR}/arxiv_list_of_dicts.json", "w"),
        )

        if os.path.exists("data/arxiv_pandoc.jsonl"):
            os.remove("data/arxiv_pandoc.jsonl")
            os.remove("data/arxiv_pandoc.txt")

        print("Converting arxiv_dict.json to arxiv.jsonl and arxiv.txt...")
        for paper in self.arxiv_list_of_dicts:
            yield paper

        # delete_unwanted_files = input(
        #     "Delete unwanted files (only keep .jsonl and main .txt files)? (y/n) "
        # )
        delete_unwanted_files = "y"
        if delete_unwanted_files == "y":
            sh("rm -rf tmp files done out outtxt")
        print("Done extracting text and metadata from arxiv entries.")

    def setup(self):

        self.PROJECT_DIR = Path(os.getcwd())
        self.RAW_DIR = Path(f"{self.PROJECT_DIR}/data/raw")
        self.INTERIM_DIR = Path(f"{self.PROJECT_DIR}/data/interim")
        self.PROCESSED_DIR = Path(f"{self.PROJECT_DIR}/data/processed")
        self.TARS_DIR = self.RAW_DIR / "tars"
        self.LATEX_DIR = self.RAW_DIR / "latex_files"
        self.RAW_CSVS_DIR = self.RAW_DIR / "csvs"
        self.ARXIV_PDFS_DIR = self.RAW_DIR / "pdfs/arxiv"
        self.PKLS_DIR = self.INTERIM_DIR / "pkls"
        self.PDFS_DIR = self.PROCESSED_DIR / "pdfs"
        self.PROCESSED_TXTS_DIR = self.PROCESSED_DIR / "txts"
        self.PROCESSED_JSONS_DIR = self.PROCESSED_DIR / "jsons"
        self.PROCESSED_CSVS_DIR = self.PROCESSED_DIR / "csvs"

        if os.path.exists(f"{self.PROCESSED_JSONS_DIR}/arxiv_dict.json"):
            self.arxiv_dict = json.load(
                open(f"{self.PROCESSED_JSONS_DIR}/arxiv_dict.json")
            )
        else:
            self.arxiv_dict = {}

        # Delete contents before starting?
        # This is useful when you are testing and want to start from scratch
        delete_contents = input("Delete data before starting? (y/n) ")
        if delete_contents == "y":
            are_you_sure = input("Are you sure? (y/n) ")
            if are_you_sure == "y":
                sh(f"rm -rf files errored fallback_needed {self.TARS_DIR}/")
        self.automatic_mode = input(
            "Automatic mode (extracts as many papers it can automatically)? (y/n): "
        )
        self.manual_mode = input(
            "Manual mode (allows manually extract the failed extractions by fixing the .tex files, giving the correct main tex filename or using detex instead of pandoc for the extraction)? (y/n): "
        )
        self.citation_level = str(
            input(
                "Citation level? (0 = original, 1 = citation of original, 2 = citation of citation, etc.): "
            )
        )
        self.remove_empty_papers = "y"  # replace with input() later

        if self.citation_level != "0":
            pass

        if self.automatic_mode == "y":
            sh(f"rm -rf tmp")
        sh("mkdir -p tmp out outtxt errored fallback_needed files")
        sh(
            "mkdir -p fallback_needed/unknown_main_tex fallback_needed/pdf_only errored/pandoc_failures errored/unknown_errors"
        )
        sh(
            f"mkdir -p {self.RAW_DIR} {self.INTERIM_DIR} {self.PROCESSED_DIR} {self.TARS_DIR} {self.RAW_CSVS_DIR} {self.LATEX_DIR} {self.PDFS_DIR}"
        )
        sh(
            f"mkdir -p {self.PKLS_DIR} {self.PROCESSED_TXTS_DIR} {self.PROCESSED_JSONS_DIR} {self.PROCESSED_CSVS_DIR}"
        )
        # arxiv_citations_dict looks like this:
        # {root_paper_id_1: [citation_paper_id_1, citation_paper_id_2, ...], ...}
        # root_paper_id_2: [citation_paper_id_1, citation_paper_id_2, ...], ...}
        # The dictionary is updated in the prepare_extracted_tars function.
        if os.path.exists(f"{self.PROCESSED_JSONS_DIR}/arxiv_citations_dict.json"):
            self.arxiv_citations_dict = json.load(
                open(f"{self.PROCESSED_JSONS_DIR}/arxiv_citations_dict.json")
            )
        else:
            self.arxiv_citations_dict = {}
            json.dump(
                self.arxiv_citations_dict,
                open(f"{self.PROCESSED_JSONS_DIR}/arxiv_citations_dict.json", "w"),
            )

        if not os.path.exists(f"{self.PKLS_DIR}/ignore_dict.pkl"):
            self._filenames_to_ignore()
        # Automatic Mode will go through all the papers in files and try
        # to convert them to markdown.
        # Non-automatic mode will go through the errored papers one by one and
        # ask the use to fix the error in the tex file to fix the conversion error.
        if self.citation_level != "0" and self.automatic_mode == "y":
            if ls("out") != [] and ls("outtxt") != []:
                sh("mv out/* data/processed/txts/")
                sh("mv outtxt/* data/processed/txts/")

        self._create_citations_csv()

        main_tex_name_list = [
            "main",
            "paper",
            "ms",
            "arxiv",
            "root",
            "example",
            "master",
            "sample",
        ]

        self.main_tex_name_substrings = [
            "nips",
            "iclr",
            "conference",
            "corl",
            "neurips",
            "icml",
        ]

        self.main_tex_name_list = [f"{item}.tex" for item in main_tex_name_list]

        wget.download("https://github.com/JayThibs/ai-safety-scrape/raw/main/ai-alignment-papers.csv", out="data/raw/csvs/ai-alignment-papers.csv")

    def download_arxiv_papers(
        self,
        pdf=False,
        create_dict_only=False,
    ):
        """
        Download arxiv papers (pdf or latex source).
        Args:
            citation_level: 0 = original, 1 = citation of original, 2 = citation of citation, etc.
            pdf: True: download pdfs instead of latex source files, False: download latex source files
            create_dict_only: True or False
        """
        if self.citation_level == "0":
            df = pd.read_csv(self.papers_csv_path, index_col=0)
            df_arxiv = df[df["Url"].str.contains("arxiv") == True]
            papers = list(set(df_arxiv["Url"].values))
            print(f"{len(papers)} papers to download")
        else:
            df = pd.read_csv(
                f"{self.PROCESSED_CSVS_DIR}/all_citations_level_{self.citation_level}.csv",
                index_col=0,
            )
            papers = list(set(list(df.index)))
            print(f"{len(papers)} papers to download")

        tars = ["None"] * len(papers)

        if ls(self.TARS_DIR):
            tars = [
                tar.split("/")[-1]
                for tar in ls(self.TARS_DIR)
                if tar.endswith(".tar.gz")
            ]
            if len(tars) != len(papers):
                # extend the tars list to match the length of the papers list
                tars = tars + ["None"] * (len(papers) - len(tars))

        incorrect_links_ids = []
        paper_dl_failures = []
        for i, (paper_link, filename) in enumerate(tqdm(zip(papers, tars))):
            paper_link = str(paper_link)
            filename = str(filename)
            paper_id = ".".join(filename.split(".")[:2])
            if (
                os.path.exists(str(self.TARS_DIR / filename))
                and create_dict_only == False
            ):
                print("Already downloaded the " + paper_id + " tar file.")
                continue

            try:
                if "/" in paper_link:
                    paper_id = paper_link.split("/")[-1]
                else:
                    paper_id = paper_link
                paper = next(arxiv.Search(id_list=[paper_id]).results())
                if (
                    self.citation_level != "0"
                    and paper.get_short_id()[:-2] in self.arxiv_dict.keys()
                ):
                    print(f"Skipping {paper_id} because it is already in dictionary.")
                    sleep(0.5) # need to add here to avoid getting banned, the "continue" statement below allows for too many quick arxiv.Search() calls
                    continue
                self.arxiv_dict[paper.get_short_id()[:-2]] = {
                    "source": "arxiv",
                    "source_filetype": "latex",
                    "converted_with": "pandoc",
                    "paper_version": str(paper.get_short_id()),
                    "post_title": paper.title,
                    "authors": [str(x) for x in paper.authors],
                    "date_published": str(paper.published),
                    "data_last_modified": str(paper.updated),
                    "url": str(paper.entry_id),
                    "abstract": paper.summary.replace("\n", " "),
                    "author_comment": paper.comment,
                    "journal_ref": paper.journal_ref,
                    "doi": paper.doi,
                    "primary_category": paper.primary_category,
                    "categories": paper.categories,
                    "citation_level": self.citation_level,
                    "main_tex_filename": "",
                    "text": "",
                    "bibliography_bbl": "",
                    "bibliography_bib": "",
                }
                tar_filename = paper.entry_id.split("/")[-1] + ".tar.gz"
                tars[i] = tar_filename
                if create_dict_only:
                    print("Added " + paper.get_short_id()[:-2] + " to json.")
                    continue
            except:
                incorrect_links_ids.append([paper_link, paper_id])
                pass
            
            try:
                sleep(0.5)
                if pdf:
                    paper.download_pdf(dirpath=str(self.ARXIV_PDFS_DIR))
                else:
                    paper.download_source(
                        dirpath=str(self.TARS_DIR), filename=tar_filename
                    )
                    print("; Downloaded paper: " + paper_id)
            except:
                print("; Could not download paper: " + paper_id)
                paper_dl_failures.append(paper_id)
                pass

        if incorrect_links_ids != []:
            print("Incorrect links:")
            print(incorrect_links_ids)
        if paper_dl_failures != []:
            print("Paper download failures:")
            print(paper_dl_failures)

        with open(f"{self.PROCESSED_JSONS_DIR}/arxiv_dict.json", "w") as fp:
            json.dump(self.arxiv_dict, fp)

        with open(self.PKLS_DIR / "arxiv_paper_tars_list.pkl", "wb") as f:
            pickle.dump(tars, f)

        with open(self.PKLS_DIR / "incorrect_links_ids_list.pkl", "wb") as f:
            pickle.dump(incorrect_links_ids, f)

        with open(self.PKLS_DIR / "paper_dl_failures_list.pkl", "wb") as f:
            pickle.dump(paper_dl_failures, f)

        return self.arxiv_dict

    def automatic_extraction(self):
        pool = mp.Pool(processes=mp.cpu_count())
        paper_tars = ls("files")
        pool.map(self._preextract_tar, paper_tars)
        pool.close()
        pool.join()
        paper_folders = ls("tmp")
        for i, paper_folder in enumerate(tqdm(paper_folders)):
            print(f"{i}/{len(paper_folders)}")
            os.chdir(self.PROJECT_DIR)
            done_paper_folder = "done/" + paper_folder.split("/")[-1]
            try:
                if os.path.exists(done_paper_folder):
                    sh(f"rm -rf {paper_folder}")
                    continue
                print(f"preparing {paper_folder}")
                self._fix_chars_in_dirs(paper_folder)
                self._prepare_extracted_tars(paper_folder)
                self._delete_style_files(
                    paper_folder
                )  # putting this here too to make sure they are deleted
                self.convert_tex(paper_dir=paper_folder)
                if os.path.exists(paper_folder):
                    sh(f"mv {paper_folder} done")
            except ExitCodeError:
                traceback.print_exc()
                print(f"Error converting {paper_folder}")

    def manual_extraction(self):
        for paper_folder in ls("errored/pandoc_failures/"):
            if os.path.isdir(paper_folder):
                sh(f"mv {paper_folder} tmp")
        for paper_folder in ls("fallback_needed/unknown_main_tex/"):
            if os.path.isdir(paper_folder):
                sh(f"mv {paper_folder} tmp")
        failed_papers = ls("tmp")
        for paper_folder in tqdm(failed_papers):
            try:
                print(f'Converting errored papers: "{paper_folder}"')
                os.chdir(self.PROJECT_DIR)
                paper_folder = os.getcwd() + "/" + paper_folder
                self.convert_tex_manual(paper_dir=paper_folder)
                sh(f"mv {paper_folder} done")
            except ExitCodeError:
                traceback.print_exc()

    def convert_tex(
        self,
        paper_dir,
        output_dir="out",
        main_tex_output_dir="outtxt",
        manual_conversion=False,
    ):
        """
        Converts paper tex file automatically. Sends errors to fallback_needed for conversion with convert_tex_semiauto.
        This function is created to work with multiprocessing. paper_dir is the directory for a specific paper in tmp once
        we've extracted the tars in tmp. An example of paper_dir is "tmp/1708.03887v2".
        """

        try:
            paper_id = paper_dir.split("/")[-1]
            if os.path.exists(f"{output_dir}/{paper_id}.md"):
                print(f"{paper_id}.md already exists.")
                try:
                    sh(f"mv {paper_dir} done")
                except ExitCodeError:
                    traceback.print_exc()
                    print(f"Error moving {paper_dir} to done.")
                    sh(f"rm -rf {paper_dir}")
                return
            os.chdir(paper_dir)
            paper_dir_full = os.getcwd()
            project_dir = "/".join(os.getcwd().split("/")[:-2])
            number_id = str(paper_id.split("v")[0])
            print("Current directory: " + os.getcwd())
            print("paper_id: " + paper_id)
            assert len(ls(".")) > 0
            self._convert_to_utf8(rootdir=".")
            paper_dir_root = ls(".")
            paper_dir_all_files = lsr(".")
            num_tex_files = num_pdf_files = root_tex_files = 0
            print(os.listdir())
            main_pdf = None
            for file in paper_dir_all_files:
                if file.endswith(".tex"):
                    num_tex_files += 1
                elif file.endswith(".pdf"):
                    if re.findall(r"(\d{4}\.\d{4,5})", file):
                        main_pdf = file
                    num_pdf_files += 1
            if num_pdf_files > 0 and num_tex_files == 0:
                print("Paper only contains PDF. Not LaTeX files. Skipping conversion.")
                os.chdir(self.PROJECT_DIR)
                self.arxiv_dict[number_id]["source_filetype"] = "pdf"
                self.arxiv_dict[number_id]["converted_with"] = ""
                json.dump(
                    self.arxiv_dict,
                    open(f"{self.PROCESSED_JSONS_DIR}/arxiv_dict.json", "w"),
                )
                sh(f"mv -f {paper_dir} fallback_needed/pdf_only")
                return
            for doc in paper_dir_root:
                if doc.endswith(".tex"):
                    root_tex_files += 1
                    main_doc = doc
            if root_tex_files == 1:
                # if there is only one tex file, use it
                sh(
                    f"if ! timeout 7s pandoc -s {main_doc} -o {paper_id}.md --wrap=none; then touch {paper_id}_pandoc_failure; fi"
                )
                if (
                    os.path.exists(f"{paper_id}_pandoc_failure")
                    and not manual_conversion
                ):
                    print(f"{paper_id} failed to convert with pandoc.")
                    os.chdir(self.PROJECT_DIR)
                    if not manual_conversion:
                        sh(f"mv -f {paper_dir} errored/pandoc_failures/")
                    return
                if manual_conversion:
                    return main_doc
                with open(f"{paper_id}.md", "r") as f:
                    paper_text = f.read()
                self.arxiv_dict[number_id]["text"] = paper_text
                self.arxiv_dict[number_id]["main_tex_filename"] = main_doc
                json.dump(
                    self.arxiv_dict,
                    open(f"{self.PROCESSED_JSONS_DIR}/arxiv_dict.json", "w"),
                )
                os.chdir(self.PROJECT_DIR)
                sh(f"mv {paper_dir}/{paper_id}.md {output_dir}/{paper_id}.md")
                # TODO: there's a better way to do this, but to make multiprocessing work,
                # I'm going to create a .txt file for each paper and store the main_tex_name in it.
                # This is a hacky way to do it, but it works. Once the extraction is done,
                # we can use the .txt file to get the main_tex_name and store it in the arxiv_dict.
                with open(f"{main_tex_output_dir}/{paper_id}.txt", "w") as f:
                    f.write(main_doc)
                return main_doc
            else:
                # if there are multiple tex files,
                # check for the main file based on a common list of names
                filenames_to_ignore = pickle.load(
                    open(f"{self.PKLS_DIR}/ignore_dict.pkl", "rb")
                )
                print(filenames_to_ignore)
                os.chdir(paper_dir_full)
                list_of_tex_files = [
                    doc.split("/")[-1] for doc in ls(".") if doc.endswith(".tex")
                ]
                print(list_of_tex_files)
                print(self.main_tex_name_list)
                matched_list = [
                    doc
                    for doc in list_of_tex_files
                    if doc.lower() in self.main_tex_name_list
                ]
                if len(matched_list) == 0:
                    # if there are no matches with main list, try substring list
                    # these are typically conference names with a lot of variations (e.g. "icml2020.tex")
                    for tex_substring in self.main_tex_name_substrings:
                        matched_list = [
                            doc
                            for doc in list_of_tex_files
                            if tex_substring in doc.lower()
                        ]
                        if len(matched_list) > 0:
                            break
                print(matched_list)
                if matched_list:
                    main_doc = matched_list[0]
                    # change to that directory and use the common file name
                    sh(
                        f"if ! timeout 7s pandoc -s {main_doc} -o {paper_id}.md --wrap=none; then touch {paper_id}_pandoc_failure; fi"
                    )
                    if (
                        os.path.exists(f"{paper_id}_pandoc_failure")
                        and not manual_conversion
                    ):
                        print(f"{paper_id} failed to convert with pandoc.")
                        os.chdir(self.PROJECT_DIR)
                        if not manual_conversion:
                            sh(f"mv -f {paper_dir} errored/pandoc_failures/")
                        return
                    if manual_conversion:
                        return main_doc
                    with open(f"{paper_id}.md", "r") as f:
                        paper_text = f.read()
                    self.arxiv_dict[number_id]["text"] = paper_text
                    self.arxiv_dict[number_id]["main_tex_filename"] = main_doc
                    json.dump(
                        self.arxiv_dict,
                        open(f"{self.PROCESSED_JSONS_DIR}/arxiv_dict.json", "w"),
                    )
                    # go back to root
                    os.chdir(self.PROJECT_DIR)
                    sh(f"mv {paper_dir}/{paper_id}.md {output_dir}/{paper_id}.md")
                    with open(f"{main_tex_output_dir}/{paper_id}.txt", "w") as f:
                        f.write(main_doc)
                    return main_doc
                else:
                    os.chdir(paper_dir_full)
                    list_of_tex_files = [
                        doc.split("/")[-1] for doc in ls(".") if doc.endswith(".tex")
                    ]
                    # if items in list_of_tex_files are in filenames_to_ignore, remove them
                    matched_list = [
                        doc
                        for doc in list_of_tex_files
                        if doc.lower() not in filenames_to_ignore
                    ]
                    print(matched_list)
                    if len(matched_list) == 1:
                        main_doc = matched_list[0]
                        # change to that directory and use the common file name
                        sh(
                            f"if ! timeout 7s pandoc -s {main_doc} -o {paper_id}.md --wrap=none; then touch {paper_id}_pandoc_failure; fi"
                        )
                        if (
                            os.path.exists(f"{paper_id}_pandoc_failure")
                            and not manual_conversion
                        ):
                            print(f"{paper_id} failed to convert with pandoc.")
                            os.chdir(self.PROJECT_DIR)
                            if not manual_conversion:
                                sh(f"mv -f {paper_dir} errored/pandoc_failures/")
                            return
                        if manual_conversion:
                            return main_doc
                        with open(f"{paper_id}.md", "r") as f:
                            paper_text = f.read()
                        self.arxiv_dict[number_id]["text"] = paper_text
                        self.arxiv_dict[number_id]["main_tex_filename"] = main_doc
                        json.dump(
                            self.arxiv_dict,
                            open(f"{self.PROCESSED_JSONS_DIR}/arxiv_dict.json", "w"),
                        )
                        # go back to root
                        os.chdir(self.PROJECT_DIR)
                        sh(f"mv {paper_dir}/{paper_id}.md {output_dir}/{paper_id}.md")
                        with open(f"{main_tex_output_dir}/{paper_id}.txt", "w") as f:
                            f.write(main_doc)
                        return main_doc

                    if self.arxiv_dict[number_id]["main_tex_filename"] != "":
                        # if main file was stored in arxiv_dict, use it
                        # arxiv_dict is created when we need to use convert_tex_semiauto and manually inputting main tex filename
                        main_doc = self.arxiv_dict[number_id]["main_tex_filename"]
                        sh(
                            f"if ! timeout 7s pandoc -s {main_doc} -o {paper_id}.md --wrap=none; then touch {paper_id}_pandoc_failure; fi"
                        )
                        if (
                            os.path.exists(f"{paper_id}_pandoc_failure")
                            and not manual_conversion
                        ):
                            print(f"{paper_id} failed to convert with pandoc.")
                            os.chdir(project_dir)
                            if not manual_conversion:
                                sh(f"mv -f {paper_dir} errored/pandoc_failures/")
                            return
                        if manual_conversion:
                            return main_doc
                        with open(f"{paper_id}.md", "r") as f:
                            paper_text = f.read()
                        self.arxiv_dict[number_id]["text"] = paper_text
                        json.dump(
                            self.arxiv_dict,
                            open(f"{self.PROCESSED_JSONS_DIR}/arxiv_dict.json", "w"),
                        )
                        os.chdir(self.PROJECT_DIR)
                        sh(f"mv {paper_dir}/{paper_id}.md out/{paper_id}.md")
                        return main_doc
                    else:
                        # can't find main file, so send to fallback_needed for manual conversion with convert_tex_semiauto
                        # it's useful to do it this way because then you can go through the fallback_needed folder and
                        # manually convert the files in a batch
                        main_doc = ""
                        if self.automatic_mode_done == False:
                            print(
                                f"{paper_id} main filename not found in main_tex_filename, sending to fallback_needed"
                            )
                            sh("touch {paper_id}_unknown_main_tex_failure")
                            os.chdir(self.PROJECT_DIR)
                            sh(f"mv -f {paper_dir} fallback_needed/unknown_main_tex/")
                        else:
                            print("Here are the possible main tex filenames:")
                            print(matched_list)
                            main_doc = input(
                                "Please enter the correct main tex filename: "
                            )
                            self.arxiv_dict[paper_id]["main_tex_filename"] = main_doc
                            os.chdir(self.PROJECT_DIR)
                            json.dump(
                                self.arxiv_dict,
                                open(
                                    f"{self.PROCESSED_JSONS_DIR}/arxiv_dict.json", "w"
                                ),
                            )
                        return main_doc

        except:
            try:
                traceback.print_exc()
                if not manual_conversion:
                    with open(f"error_log.txt", "a") as f:
                        f.write(f"{traceback.format_exc()}")
                    with open(f"{self.PROJECT_DIR}/error_log.txt", "a") as f:
                        f.write(f"{paper_id}\n {traceback.format_exc()}\n")
                    print("Error converting paper. Moving to fallback pile...")
                    os.chdir(self.PROJECT_DIR)
                    print(f"Error: Current directory: {os.getcwd()}")
                    if os.path.exists(f"{paper_dir}_pandoc_failure"):
                        sh(f"mv -f {paper_dir} errored/pandoc_failures/")
                    else:
                        sh(f"mv -f {paper_dir} errored/unknown_errors/")
                    pass
            except:
                traceback.print_exc()
                print("Error moving paper to fallback pile.")
                pass

    def convert_tex_manual(self, paper_dir):
        """
        Puts papers from fallback_needed/pandoc_failures in a queue to be
        converted with convert_tex_manual. This function is run when pandoc fails
        to convert a paper. This is typically because of some missing braces or brackets
        in the tex file. You will need to go into the main tex file and manually
        fix the issue in the file. convert_tex will be ran once in order to show you
        the error so that it's a bit clearer what you need to fix.
        Then, click enter in the terminal to continue.
        """
        fixed_error = False
        paper_id = paper_dir.split("/")[-1]
        while fixed_error == False:
            try:
                os.chdir(paper_dir)
                if os.path.exists(f"{paper_id}_pandoc_failure"):
                    sh(f"rm -f {paper_id}_pandoc_failure")
                    main_doc = self.arxiv_dict[paper_id]["main_tex_filename"]
                    print(
                        f"Opening {main_doc} in text editor. Please fix the error. Save the file once you are done. (On the first try, just press enter to run the conversion so that you can see the error.)"
                    )
                    sh(f"open {main_doc}")
                    input("Press enter to try converting the paper.")
                if os.path.exists(f"{paper_id}_unknown_main_tex_failure"):
                    sh(f"rm -f {paper_id}_unknown_main_tex_failure")
                    print(
                        f"The main tex filename is unknown. Press enter to run the conversion and manually enter the filename."
                    )
                    # We run the conversion once to save the correct main tex filename, then run it again to convert the paper.
                    main_doc = self.convert_tex(paper_dir, manual_conversion=True)
                main_doc = self.convert_tex(paper_dir, manual_conversion=True)
            except:
                print(
                    "Error converting the paper. Please fix the error in the tex file."
                )
                traceback.print_exc()
                pass

            print("Was the error fixed? (y/n)")
            answer = input()
            if answer == "n":
                print("Would you like to use detex instead of pandoc? (y/n)")
                detex_answer = input()
                if detex_answer == "y":
                    os.chdir(paper_dir)
                    sh(f"detex {main_doc} > {paper_id}.md")
                    # open detexed md file to clean it up
                    with open(f"{paper_id}.md", "r") as f:
                        paper_text = f.read()
                    paper_text = re.sub(r"\n\s+\n", "\n", paper_text)
                    paper_text = re.sub("\n{1,}", "\n\n", paper_text)
                    with open(f"{paper_id}.md", "w") as f:
                        f.write(paper_text)
                    fixed_error = True
                    os.chdir(self.PROJECT_DIR)
                    sh(f"mv {paper_dir}/{paper_id}.md out/{paper_id}.md")
                    break
            if answer == "y":
                fixed_error = True
                os.chdir(self.PROJECT_DIR)
                sh(f"mv {paper_dir}/{paper_id}.md out/{paper_id}.md")
                break
            else:
                input(
                    "Press enter once you have fixed the error and fixed the tex file."
                )
                continue

    def insert_text_in_dict(self, mdfile):
        mdfile = mdfile.split("/")[-1]
        id = mdfile.split("v")[0]
        try:
            with open(f"out/{mdfile}", "r") as f:
                text = f.read()
            self.arxiv_dict[id]["text"] = text
            self.arxiv_dict[id]["good_extraction"] = True
        except ExitCodeError and KeyError:
            traceback.print_exc()
            if id in self.arxiv_dict:
                self.arxiv_dict[id]["good_extraction"] = False
            print(f"Error reading {mdfile}. May not exist.")

    def insert_main_tex_in_dict(self, main_tex_name_txt):
        try:
            # load main_tex_name_txt
            with open(f"{main_tex_name_txt}", "r") as f:
                main_tex_name = f.read()
            arxiv_id = main_tex_name_txt.split("/")[-1].split("v")[0]
            self.arxiv_dict[arxiv_id]["main_tex_filename"] = main_tex_name.split("/")[
                -1
            ]
        except ExitCodeError and KeyError:
            traceback.print_exc()
            print(f"Error reading {main_tex_name_txt}. May not exist.")

    def _create_citations_csv(self):
        """
        Create a csv file with all the arxiv citations for each paper.
        """
        new_citation_level = str(int(self.citation_level) + 1)
        print(
            f"Citation level is {self.citation_level}, so we'll create a CSV of the papers at the next citation level ({new_citation_level})."
        )
        all_citations = {}
        for paper_id in self.arxiv_citations_dict.keys():
            for citation in self.arxiv_citations_dict[paper_id].keys():
                if citation not in self.arxiv_dict:
                    all_citations[citation] = True
        all_citations = pd.DataFrame(list(all_citations.keys()))
        all_citations.to_csv(
            f"{self.PROCESSED_CSVS_DIR}/all_citations_level_{new_citation_level}.csv",
            index=False,
        )
        print(f"Saved CSV of all citations at level {new_citation_level}.")

    @staticmethod
    def _fix_chars_in_dirs(parent):
        for path, folders, files in os.walk(parent):
            for f in files:
                os.rename(
                    os.path.join(path, f), os.path.join(path, f.replace(" ", "_"))
                )
            for folder in folders:
                new_folder_name = folder.translate(
                    {ord(c): "_" for c in " !@#$%^&*()[]{};:,<>?\|`~-=+"}
                )
                if new_folder_name != folder:
                    os.rename(
                        os.path.join(path, folder), os.path.join(path, new_folder_name)
                    )

    @staticmethod
    def _preextract_tar(tar_filepath, output_dir="tmp"):
        """
        Creates tmp/{tar_name} directory and extracts tar files and copies them to tmp/tar_name/*.
        Creates tmp/done_{tar_name} file to signal copy_tar that extraction is done.
        """
        tar_name = tar_filepath.split("/")[-1][:-7]
        if os.path.exists(f"{output_dir}/{tar_name}"):
            print(f"{tar_name} already extracted.")
            return
        sh(
            f"(mkdir -p {output_dir}/{tar_name}; tar xf {tar_filepath} -C {output_dir}/{tar_name}; echo finished preload of {tar_name}) &"
        )

    def _prepare_extracted_tars(self, paper_dir_path):
        # extracts tar files to tmp/{dump_name}/*
        paper_id = paper_dir_path.split("/")[-1]
        try:
            # load arxiv_citations_dict json to add citations to paper_id
            self.arxiv_citations_dict = json.load(
                open(f"{self.PROCESSED_JSONS_DIR}/arxiv_citations_dict.json")
            )
            try:
                for doc in lsr(paper_dir_path):
                    if doc.endswith(".gz"):
                        sh(f"gunzip {doc}")
                for doc in lsr(paper_dir_path):
                    if doc.endswith(".tar"):
                        # if tarfile, extract in {doc[:-3]}_extract folder and delete tarfile
                        sh(
                            f"mkdir -p {doc[:-3]}_extract && tar xf {doc[:-3]} -C {doc[:-3]}_extract"
                        )
                        sh(f"rm {doc[:-3]}")
            except:
                pass
            for doc in lsr(paper_dir_path):
                try:
                    if doc.endswith(".tex"):
                        # if tex, do nothing and keep it
                        pass

                    elif doc.endswith(".sty"):
                        # if sty, delete it since it causes issues with pandoc
                        # this file is a LaTeX Style document
                        # (commonly used for formatting for a specific journal/conference)
                        sh(f"rm {doc}")

                    elif doc.endswith(".bbl") or doc.endswith(".bib"):
                        # if bbl, extract arxiv ids from citations, add to list, and delete bbl
                        arxiv_citations, bibliography = self._get_arxiv_ids(doc)
                        if len(arxiv_citations) > 0:
                            for arxiv_id in arxiv_citations:
                                if self.arxiv_citations_dict.get(paper_id) is None:
                                    self.arxiv_citations_dict[paper_id] = {
                                        arxiv_id: True
                                    }
                                else:
                                    self.arxiv_citations_dict[paper_id].update(
                                        {arxiv_id: True}
                                    )
                            json.dump(
                                self.arxiv_citations_dict,
                                open(
                                    f"{self.PROCESSED_JSONS_DIR}/arxiv_citations_dict.json",
                                    "w",
                                ),
                            )
                            id = paper_id.split("v")[0]  # remove version number
                            self.arxiv_dict[id][
                                "arxiv_citations"
                            ] = self.arxiv_citations_dict[paper_id]
                        if doc.endswith(".bbl"):
                            self.arxiv_dict[id]["bibliography_bbl"] = bibliography
                        elif doc.endswith(".bib"):
                            self.arxiv_dict[id]["bibliography_bib"] = bibliography
                        json.dump(
                            self.arxiv_dict,
                            open(f"{self.PROCESSED_JSONS_DIR}/arxiv_dict.json", "w"),
                        )

                    # check if filename has no extension, this is likely a .tex file
                    # if so, add .tex to the filename
                    # these files are typically named with the arxiv id (e.g. 1801.01234)
                    elif re.findall(
                        r"(\d{4}\.\d{4,5})", doc.split("/")[-1]
                    ) != [] and not doc.endswith(".pdf"):
                        # add .tex to filename
                        sh(f"mv {doc} {doc}.tex")

                    elif doc.endswith(".DS_Store"):
                        # delete .DS_Store files
                        sh(f"rm {doc}")

                    else:
                        pass
                        # if not .tex or .bbl, just delete file
                        # sh(f"rm {doc}")
                except ExitCodeError:
                    traceback.print_exc()
                    print(f"Error deleting file: {doc}")
        except Exception:
            traceback.print_exc()
            print(f"Error deleting files in {paper_id}")

    @staticmethod
    def _delete_style_files(paper_dir_path):
        # delete all files with .sty extension
        for doc in lsr(paper_dir_path):
            if doc.endswith(".sty"):
                sh(f"rm {doc}")

    @staticmethod
    def _any_to_utf8(b):
        """Detects encoding and converts to utf-8."""
        try:
            return b.decode("utf-8")
        except UnicodeDecodeError:
            # try to figure out encoding if not utf-8
            guess = chardet.detect(b)["encoding"]
            if not guess or guess == "UTF-8":
                return
            try:
                return b.decode(guess)
            except (UnicodeDecodeError, LookupError):
                # still cant figure out encoding, give up
                return

    def _convert_to_utf8(self, rootdir="."):
        """Converts all files in root folder to utf-8."""
        for doc in ls(rootdir):
            if doc.endswith(".tex"):
                try:
                    with open(doc, "rb") as fh:
                        b = fh.read()
                        cont = self._any_to_utf8(b)
                        if cont is None:
                            return
                    fwrite(doc, cont)
                except ExitCodeError:
                    traceback.print_exc()
                    print(f"Error converting {doc}, will go to /fallback_needed.")
                    print("Error converting files to utf-8.")

    @staticmethod
    def _mv_files_to_root(rootdir="tmp"):
        """Moves all files in root folder subdirectories to root folder."""
        for doc in ls(rootdir):
            try:
                if os.path.isdir(doc):
                    sh(f"find ./{doc} -type f -print0 | xargs -0 mv -t .")
                    sh(f"rm -rf {doc}")
            except ExitCodeError:
                traceback.print_exc()
                print(
                    "Error moving files to root folder. Likely because there's a file with the same name in the root folder."
                )

    @staticmethod
    def _get_arxiv_ids(bib_file_path):
        with open(bib_file_path, "r") as f:
            bib_string = f.read()
        return re.findall(r"(?:arXiv:|abs/)(\d{4}\.\d{4,5})", bib_string), bib_string

    @staticmethod
    def _count_empty_mds(paper_dir):
        files = ls(paper_dir)
        empty_files = []
        for file in files:
            file.split(".")[-1]
            if file.endswith(".md"):
                if os.stat(file).st_size == 0:
                    empty_files.append(file)

        return empty_files, files

    def _mv_empty_mds(self):
        sh("mkdir -p fallback_needed/empty_mds")
        empty_files, files = self._count_empty_mds("out")
        num_empty_files = len(empty_files)
        print(f"{num_empty_files} empty files out of {len(files)}")
        print(empty_files)

        for file in empty_files:
            folder = "done/" + file.split("/")[-1][:-3] + "/"
            sh(f"mv {file} {folder}")
            sh(f"mv {folder} fallback_needed/empty_mds/")

        print("Done moving empty files to fallback_needed/empty_mds")

    def _remove_empty_mds_from_dict(self):
        empty_mds = [
            empty_md.split("/")[-1][:-2] for empty_md in ls("fallback_needed/empty_mds")
        ]
        print("Removing the following papers from dict since the contents are empty: ")
        print(empty_mds)
        for empty_md in empty_mds:
            self.arxiv_dict.pop(empty_md, None)
        return self.arxiv_dict

    def _remove_empty_texts_from_dict(self):
        total_papers = len(self.arxiv_dict)
        removed_papers = 0
        paper_ids = list(self.arxiv_dict.keys())
        for paper_id in paper_ids:
            if (
                len(self.arxiv_dict[paper_id]["text"]) < 500
                and self.arxiv_dict[paper_id]["main_tex_filename"] != ""
            ):
                removed_papers += 1
                self.arxiv_dict.pop(paper_id, None)
        print(f"{removed_papers} out of {total_papers} papers removed")
        return self.arxiv_dict

    def _filenames_to_ignore(self):
        ignore_list_title = [
            "Approach",
            "Conclusion",
            "Experiments",
            "Figures",
            "Implementation",
            "Appendix",
            "Introduction",
            "Preliminaries",
            "Problem",
            "RelatedWork",
            "RelatedWorks",
            "Related",
            "Background",
            "Methods",
            "math_commands",
            "Results",
            "Supplement",
            "Abstract",
            "Discussion",
            "Evaluation",
            "Methodology",
            "mathcommands",
            "Prelim",
            "Related_Work",
            "Method",
            "Intro",
            "Proofs",
            "Macros",
            "Pseudocode",
            "Conc",
            "Exp",
            "Symbol",
            "Custom",
            "Packages",
            "Glossary",
            "Experiment",
            "Dataset",
            "Model",
            "Concl",
            "Experim",
            "Acks",
            "Data",
            "Metrics",
            "Train",
            "Defs",
            "Defn",
            "Comments",
            "Acknowledgements",
            "Analysis",
            "Summary",
            "Background",
            "Theory",
            "Abbrev",
            "Plots",
            "Datasheet",
            "References",
            "Supp",
        ]

        ignore_list = self._modify_caps(ignore_list_title)
        df_ignore = pd.DataFrame(ignore_list)
        df_ignore.to_csv(
            f"{self.RAW_CSVS_DIR}/ignore_filenames.csv", index=False, header=False
        )
        ignore_dict = self._csv_to_dict(f"{self.RAW_CSVS_DIR}/ignore_filenames.csv")
        if "Approached" in ignore_dict:
            print("Approach is in ignore_dict")
        else:
            print("Approach is not in ignore_dict")

        with open(f"{self.PKLS_DIR}/ignore_dict.pkl", "wb") as f:
            pickle.dump(ignore_dict, f)

    @staticmethod
    def _modify_caps(ignore_list_title):
        ignore_list_lower = []
        for item in ignore_list_title:
            ignore_list_lower.append(f"{item.lower()}.tex")
        return ignore_list_lower

    @staticmethod
    def _csv_to_dict(csv_file):
        """
        Opens a csv file and returns a dictionary of the contents.
        """
        with open(csv_file) as f:
            ignore_dict = {}
            reader = csv.reader(f)
            for row in reader:
                ignore_dict[row[0]] = True
            return ignore_dict

