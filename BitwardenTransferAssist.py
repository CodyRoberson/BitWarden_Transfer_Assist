"""
This is a tkinter based GUI that facilitates the manual migration of
password entries from Bitwarden into a JSON file that can be parsed by Bitwarden.

This only uses python built-in libraries, so it should work in any standard python 3 installation without
needing to install any dependencies. Just run this script, and it will create a data.json file in the same
directory to store the entries. You can then import that file into Bitwarden using the "Bitwarden (json)" format.

"""

import json
import os
import uuid
import tkinter
import tkinter.messagebox
import tkinter.ttk


class GUI:
    DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")

    def __init__(self, master):
        self.master = master
        master.title("Shitwarden Migration Tool")
        master.geometry("850x675")
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1, minsize=280)
        master.grid_columnconfigure(1, weight=2, minsize=520)

        self.data = self.load_data()
        self.current_edit_id = None

        self.left_frame = tkinter.Frame(master, padx=10, pady=10)
        self.left_frame.grid(row=0, column=0, sticky="nsew")
        self.left_frame.grid_rowconfigure(1, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)

        self.right_frame = tkinter.Frame(master, padx=10, pady=10)
        self.right_frame.grid(row=0, column=1, sticky="nsew")
        self.right_frame.grid_columnconfigure(1, weight=1)

        self.create_entry_list()
        self.create_form()
        self.refresh_tree()

    def create_entry_list(self):
        self.tree_label = tkinter.Label(self.left_frame, text="Saved Entries:")
        self.tree_label.grid(row=0, column=0, sticky="w")

        self.tree = tkinter.ttk.Treeview(
            self.left_frame,
            columns=("Name",),
            show="headings",
            selectmode="browse",
            height=25,
        )
        self.tree.heading("Name", text="Name")
        self.tree.column("Name", anchor="w")
        self.tree.grid(row=1, column=0, sticky="nsew", pady=(6, 6))
        self.tree.bind("<Double-1>", self.on_tree_double_click)

        self.tree_scroll = tkinter.ttk.Scrollbar(
            self.left_frame, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=self.tree_scroll.set)
        self.tree_scroll.grid(row=1, column=1, sticky="ns")

        self.delete_button = tkinter.Button(
            self.left_frame,
            text="Delete Selected",
            command=self.delete_selected,
        )
        self.delete_button.grid(row=2, column=0, sticky="ew")

    def create_form(self):
        label_options = {"anchor": "w"}

        self.item_name_label = tkinter.Label(self.right_frame, text="Item Name:", **label_options)
        self.item_name_label.grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.item_name_entry = tkinter.Entry(self.right_frame)
        self.item_name_entry.grid(row=0, column=1, sticky="ew", pady=(0, 4))

        self.username_label = tkinter.Label(self.right_frame, text="Username:", **label_options)
        self.username_label.grid(row=1, column=0, sticky="w", pady=(0, 4))
        self.username_entry = tkinter.Entry(self.right_frame)
        self.username_entry.grid(row=1, column=1, sticky="ew", pady=(0, 4))

        self.password_label = tkinter.Label(self.right_frame, text="Password:", **label_options)
        self.password_label.grid(row=2, column=0, sticky="w", pady=(0, 4))
        self.password_entry = tkinter.Entry(self.right_frame)
        self.password_entry.grid(row=2, column=1, sticky="ew", pady=(0, 4))

        self.authenticator_label = tkinter.Label(
            self.right_frame, text="Authenticator Key:", **label_options
        )
        self.authenticator_label.grid(row=3, column=0, sticky="w", pady=(0, 4))
        self.authenticator_entry = tkinter.Entry(self.right_frame)
        self.authenticator_entry.grid(row=3, column=1, sticky="ew", pady=(0, 4))

        self.url_label = tkinter.Label(self.right_frame, text="Website URL:", **label_options)
        self.url_label.grid(row=4, column=0, sticky="w", pady=(0, 4))
        self.url_entry = tkinter.Entry(self.right_frame)
        self.url_entry.grid(row=4, column=1, sticky="ew", pady=(0, 4))

        self.notes_label = tkinter.Label(self.right_frame, text="Notes:", **label_options)
        self.notes_label.grid(row=5, column=0, sticky="nw", pady=(0, 4))
        self.notes_entry = tkinter.Text(self.right_frame, width=40, height=8, borderwidth=2, relief="solid")
        self.notes_entry.grid(row=5, column=1, sticky="ew", pady=(0, 4))

        self.save_button = tkinter.Button(
            self.right_frame, text="Save", command=self.save_entry
        )
        self.save_button.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(8, 0))

    def load_data(self):
        if not os.path.exists(self.DATA_FILE):
            return {"folders": [], "items": []}

        try:
            with open(self.DATA_FILE, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (json.JSONDecodeError, OSError):
            return {"folders": [], "items": []}

        if not isinstance(data, dict):
            data = {"folders": [], "items": []}

        data.setdefault("folders", [])
        data.setdefault("items", [])
        return data

    def save_data(self):
        with open(self.DATA_FILE, "w", encoding="utf-8") as handle:
            json.dump(self.data, handle, indent=2)

    def get_imported_folder_id(self):
        for folder in self.data.get("folders", []):
            if folder.get("name") == "Imported" and folder.get("id"):
                return folder["id"]

        folder_id = str(uuid.uuid4())
        self.data.setdefault("folders", []).append(
            {"id": folder_id, "name": "Imported"}
        )
        return folder_id

    def refresh_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for entry in self.data.get("items", []):
            name = entry.get("name", "(Unnamed)")
            item_id = entry.get("id") or str(uuid.uuid4())
            self.tree.insert("", "end", iid=item_id, values=(name,))

    def clear_form(self):
        self.item_name_entry.delete(0, tkinter.END)
        self.username_entry.delete(0, tkinter.END)
        self.password_entry.delete(0, tkinter.END)
        self.authenticator_entry.delete(0, tkinter.END)
        self.url_entry.delete(0, tkinter.END)
        self.notes_entry.delete("1.0", tkinter.END)
        self.current_edit_id = None

    def has_form_content(self):
        return any(
            field.strip()
            for field in [
                self.item_name_entry.get(),
                self.username_entry.get(),
                self.password_entry.get(),
                self.authenticator_entry.get(),
                self.url_entry.get(),
                self.notes_entry.get("1.0", tkinter.END),
            ]
        )

    def load_item_into_form(self, entry):
        self.item_name_entry.delete(0, tkinter.END)
        self.item_name_entry.insert(0, entry.get("name", ""))

        login = entry.get("login", {})
        self.username_entry.delete(0, tkinter.END)
        self.username_entry.insert(0, login.get("username", ""))

        self.password_entry.delete(0, tkinter.END)
        self.password_entry.insert(0, login.get("password", ""))

        self.authenticator_entry.delete(0, tkinter.END)
        self.authenticator_entry.insert(0, login.get("totp", ""))

        self.url_entry.delete(0, tkinter.END)
        uris = login.get("uris", [])
        self.url_entry.insert(0, uris[0].get("uri", "") if uris else "")

        self.notes_entry.delete("1.0", tkinter.END)
        self.notes_entry.insert("1.0", entry.get("notes", ""))

    def on_tree_double_click(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        item_id = selected[0]
        if self.has_form_content() and self.current_edit_id != item_id:
            confirm = tkinter.messagebox.askyesno(
                "Overwrite form",
                "The current form already contains text. Overwrite it with the selected item?",
            )
            if not confirm:
                return

        matching = next((item for item in self.data.get("items", []) if item.get("id") == item_id), None)
        if not matching:
            return

        self.load_item_into_form(matching)
        self.current_edit_id = item_id

    def save_entry(self):
        item_name = self.item_name_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        authenticator_key = self.authenticator_entry.get().strip()
        url = self.url_entry.get().strip()
        notes = self.notes_entry.get("1.0", tkinter.END).strip()

        if not item_name:
            tkinter.messagebox.showwarning("Missing name", "Please enter an item name before saving.")
            return

        if self.current_edit_id:
            updated = False
            for item in self.data.setdefault("items", []):
                if item.get("id") == self.current_edit_id:
                    item["name"] = item_name
                    item["notes"] = notes
                    item["login"] = {
                        "uris": [{"match": None, "uri": url}] if url else [],
                        "username": username,
                        "password": password,
                        "totp": authenticator_key,
                    }
                    updated = True
                    break

            if not updated:
                # Fallback if the item disappeared from the list
                self.data["items"].append({
                    "id": self.current_edit_id,
                    "organizationId": None,
                    "folderId": self.get_imported_folder_id(),
                    "type": 1,
                    "reprompt": 0,
                    "name": item_name,
                    "notes": notes,
                    "favorite": False,
                    "login": {
                        "uris": [{"match": None, "uri": url}] if url else [],
                        "username": username,
                        "password": password,
                        "totp": authenticator_key,
                    },
                    "collectionIds": None,
                })
        else:
            new_item = {
                "id": str(uuid.uuid4()),
                "organizationId": None,
                "folderId": self.get_imported_folder_id(),
                "type": 1,
                "reprompt": 0,
                "name": item_name,
                "notes": notes,
                "favorite": False,
                "login": {
                    "uris": [{"match": None, "uri": url}] if url else [],
                    "username": username,
                    "password": password,
                    "totp": authenticator_key,
                },
                "collectionIds": None,
            }
            self.data.setdefault("items", []).append(new_item)

        self.save_data()
        self.refresh_tree()
        self.clear_form()

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            tkinter.messagebox.showwarning(
                "No selection", "Please select an entry before attempting to delete."
            )
            return

        item_id = selected[0]
        confirm = tkinter.messagebox.askyesno(
            "Delete entry",
            "Delete the selected entry from data.json?",
        )
        if not confirm:
            return

        self.data["items"] = [
            item for item in self.data.get("items", []) if item.get("id") != item_id
        ]
        self.save_data()
        self.refresh_tree()


if __name__ == "__main__":
    root = tkinter.Tk()
    gui = GUI(root)
    root.mainloop()
