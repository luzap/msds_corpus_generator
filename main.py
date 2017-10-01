import os
import csv
from datetime import date
import urllib.request
import tkinter as tk
import multiprocessing

import PyPDF2 as pdf


class Object:
    """Container for generic object."""

    def __init__(self, obj_class: str, obj_brand: str, obj: str, link: str,
                 date: str):
        self.obj_class = obj_class.lower()
        self.brand = obj_brand
        self.obj = obj
        self.link = link
        self.date = date

    def __repr__(self):
        return "<{clss}>: {brand}, {obj}".format(clss=self.obj_class,
                                                 brand=self.brand if self.brand != "" else "Material",
                                                 obj=self.obj)

    def get_name(self):
        return ((obj.brand.lower() if obj.brand else "material") +
                "_" + obj.obj.lower()).replace(" ", "_")


def download_pdf(obj):
    """Downloads PDF documents found at the given links."""
    dirs = "{}".format(obj.obj_class)

    if not os.path.isdir(dirs):
        os.makedirs(dirs)

    with open(os.path.join(dirs, obj.get_name() + ".pdf"), "wb") as pdffile:
        try:
            request = urllib.request.urlopen(obj.link)
            pdffile.write(request.read())
        except Exception as e:
            print(e)


class Window:

    filename = "inventory.csv"
    listing = []
    headers = ["Class", "Brand", "Object", "Link", "Date"]

    def __init__(self, master):
        self.frame = tk.Frame(master)
        self.frame.pack()

        def save():
            self.write_to_csv()
            master.destroy()

        master.protocol("WM_DELETE_WINDOW", save)

        tk.Label(self.frame, text="Class").grid(row=0)
        tk.Label(self.frame, text="Brand").grid(row=1)
        tk.Label(self.frame, text="Object").grid(row=2)
        tk.Label(self.frame, text="Link").grid(row=3)
        tk.Label(self.frame, text="Date").grid(row=4)

        self.class_var = tk.StringVar()
        self.brand_var = tk.StringVar()
        self.obj_var = tk.StringVar()
        self.link_var = tk.StringVar()
        self.date_var = tk.StringVar()

        self.class_entry = tk.Entry(self.frame, textvariable=self.class_var)
        self.brand_entry = tk.Entry(self.frame, textvariable=self.brand_var)
        self.obj_entry = tk.Entry(self.frame, textvariable=self.obj_var)
        self.link_entry = tk.Entry(self.frame, textvariable=self.link_var)
        self.date_entry = tk.Entry(self.frame, textvariable=self.date_var)

        self.class_entry.grid(row=0, column=1)
        self.brand_entry.grid(row=1, column=1)
        self.obj_entry.grid(row=2, column=1)
        self.link_entry.grid(row=3, column=1)
        self.date_entry.grid(row=4, column=1)

        self.add_button = tk.Button(self.frame,
                                    text="Add", command=self.add_object)

        self.download_button = tk.Button(self.frame,
                                         text="Download all PDF",
                                         command=self.download_all)

        self.add_button.grid(row=5)
        self.download_button.grid(row=5, column=1)

    def add_object(self):
        self.listing.append(Object(
            self.class_entry.get(), self.brand_entry.get(), self.obj_var.get(),
            self.link_var.get(), self.date_var.get())
        )

    def write_to_csv(self):
        self.listing = sorted(
            self.listing, key=lambda x: (x.obj_class, x.brand))
        with open(self.filename, 'w') as csvfile:
            writer = csv.writer(csvfile, dialect='excel', lineterminator='\n')
            writer.writerow(self.headers)
            for entry in self.listing:
                writer.writerow([entry.obj_class, entry.brand,
                                 entry.obj, entry.link, entry.date])

    def read_from_csv(self) -> list:
        with open(self.filename, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row != self.headers:
                    self.listing.append(Object(*row))

    def download_all(self) -> None:
        # TODO Grey out all fields when downloading
        pool = multiprocessing.Pool()
        pool.map(download_pdf, self.listing)
        pool.close()
        pool.join()

    def merge_pdfs(self) -> None:
        pass


if __name__ == '__main__':
    root = tk.Tk()
    root.title("MSDS Corpus")
    root.resizable(width=False, height=False)

    window = Window(root)
    window.read_from_csv()

    tk.mainloop()
