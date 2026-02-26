"""
DICOM Tag Viewer Dialog

Provides a dialog for viewing all DICOM tags from a file or dataset,
including private tags.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

try:
    from .tag import get_all_tags_from_file, get_all_tags_from_dataset, get_tag_statistics, format_tag_list
except ImportError:
    from tag import get_all_tags_from_file, get_all_tags_from_dataset, get_tag_statistics, format_tag_list


class TagViewerDialog(tk.Toplevel):
    """Dialog for viewing all DICOM tags from a file or dataset."""
    
    def __init__(self, parent, logger, filepath=None, dataset=None):
        """
        Initialize tag viewer dialog.
        
        Args:
            parent: Parent window
            logger: Logger instance
            filepath: Optional path to DICOM file
            dataset: Optional pydicom Dataset to display
        """
        super().__init__(parent)
        self.logger = logger
        self.filepath = filepath
        self.dataset = dataset
        self.all_tags = []
        
        self.title("DICOM Tag Viewer")
        self.geometry("1200x700")
        self.resizable(True, True)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        self._build_ui()
        
        # Load data if provided
        if filepath or dataset:
            self._load_tag_data()
    
    def _build_ui(self):
        """Build the dialog UI."""
        # Title
        title_frame = ttk.Frame(self)
        title_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(title_frame, text="DICOM Tag Viewer - All Tags", 
                 font=("Arial", 12, "bold")).pack()
        
        # Control frame
        control_frame = ttk.Frame(self)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Left side - File selection
        left_frame = ttk.Frame(control_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(left_frame, text="Load DICOM File", 
                  command=self._load_file).pack(side=tk.LEFT, padx=2)
        
        # Show private tags checkbox
        self.show_private_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(left_frame, text="Show Private Tags", 
                       variable=self.show_private_var,
                       command=self._filter_tags).pack(side=tk.LEFT, padx=10)
        
        # Right side - Search
        right_frame = ttk.Frame(control_frame)
        right_frame.pack(side=tk.RIGHT)
        
        ttk.Label(right_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._on_search_changed)
        search_entry = ttk.Entry(right_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(right_frame, text="Clear", command=self._clear_search).pack(side=tk.LEFT, padx=2)
        
        # Info label
        self.info_label = ttk.Label(self, text="No file loaded")
        self.info_label.pack(fill=tk.X, padx=10, pady=5)
        
        # Tree frame with scrollbars
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        
        # Create treeview with columns
        columns = ("Tag", "Name", "VR", "VM", "Value", "Type")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="tree headings", height=25)
        
        # Configure column headings and widths
        self.tree.heading("#0", text="Level")
        self.tree.heading("Tag", text="Tag", command=lambda: self._sort_by_column("Tag", False))
        self.tree.heading("Name", text="Name", command=lambda: self._sort_by_column("Name", False))
        self.tree.heading("VR", text="VR", command=lambda: self._sort_by_column("VR", False))
        self.tree.heading("VM", text="VM", command=lambda: self._sort_by_column("VM", False))
        self.tree.heading("Value", text="Value", command=lambda: self._sort_by_column("Value", False))
        self.tree.heading("Type", text="Type", command=lambda: self._sort_by_column("Type", False))
        
        self.tree.column("#0", width=100, anchor="w")
        self.tree.column("Tag", width=120, anchor="center")
        self.tree.column("Name", width=250, anchor="w")
        self.tree.column("VR", width=50, anchor="center")
        self.tree.column("VM", width=50, anchor="center")
        self.tree.column("Value", width=400, anchor="w")
        self.tree.column("Type", width=80, anchor="center")
        
        # Add scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="Export to Text", 
                  command=self._export_to_text).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Statistics", 
                  command=self._show_statistics).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Refresh", 
                  command=self._load_tag_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Close", 
                  command=self.destroy).pack(side=tk.RIGHT, padx=5)
    
    def _load_file(self):
        """Load a DICOM file."""
        filepath = filedialog.askopenfilename(
            title="Select DICOM file",
            filetypes=[("DICOM Files", "*.dcm;*.dicom;*"), ("All Files", "*.*")]
        )
        
        if filepath:
            self.filepath = filepath
            self.dataset = None  # Clear dataset
            self._load_tag_data()
    
    def _load_tag_data(self):
        """Load and display DICOM tags."""
        try:
            # Determine source
            if self.filepath:
                success, result = get_all_tags_from_file(self.filepath, logger=self.logger)
                source_info = f"File: {self.filepath}"
            elif self.dataset:
                success, result = get_all_tags_from_dataset(self.dataset, logger=self.logger)
                source_info = "Current Dataset"
            else:
                self.info_label.config(text="No file or dataset to load")
                return
            
            if not success:
                self.info_label.config(text=f"Error: {result}")
                messagebox.showerror("Tag Viewer Error", result)
                return
            
            # Store all tags
            self.all_tags = result
            
            # Display tags
            self._populate_tree()
            
            # Update info
            stats = get_tag_statistics(self.all_tags)
            self.info_label.config(
                text=f"{source_info} - {stats['total']} tags "
                     f"({stats['public']} public, {stats['private']} private)"
            )
            
            self.logger.info(f"Loaded {stats['total']} tags from DICOM")
        
        except Exception as e:
            error_msg = f"Failed to load tags: {e}"
            self.info_label.config(text=error_msg)
            self.logger.exception("Failed to load DICOM tags")
            messagebox.showerror("Tag Viewer Error", error_msg)
    
    def _populate_tree(self):
        """Populate tree with tags."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get filter settings
        show_private = self.show_private_var.get()
        search_text = self.search_var.get().lower()
        
        # Add tags
        count = 0
        for tag_dict in self.all_tags:
            # Apply filters
            if not show_private and tag_dict['is_private']:
                continue
            
            if search_text and not self._matches_search(tag_dict, search_text):
                continue
            
            # Determine type
            tag_type = "Private" if tag_dict['is_private'] else "Public"
            
            # Get prefix (for sequence nesting)
            prefix = tag_dict.get('prefix', '')
            level_text = prefix if prefix else "Root"
            
            # Add to tree
            item_id = self.tree.insert("", "end", text=level_text, values=(
                tag_dict['tag'],
                tag_dict['name'],
                tag_dict['vr'],
                tag_dict['vm'],
                tag_dict['value'],
                tag_type
            ))
            
            # Style private tags differently
            if tag_dict['is_private']:
                self.tree.item(item_id, tags=("private",))
            
            count += 1
        
        # Configure styling
        self.tree.tag_configure("private", foreground="blue")
        
        # Update info with filtered count
        if search_text or not show_private:
            stats = get_tag_statistics(self.all_tags)
            self.info_label.config(
                text=f"Showing {count} of {stats['total']} tags "
                     f"({stats['public']} public, {stats['private']} private)"
            )
    
    def _matches_search(self, tag_dict, search_text):
        """Check if tag matches search text."""
        return (search_text in tag_dict['tag'].lower() or
                search_text in tag_dict['name'].lower() or
                search_text in tag_dict['value'].lower())
    
    def _filter_tags(self):
        """Apply filters and refresh display."""
        self._populate_tree()
    
    def _on_search_changed(self, *args):
        """Handle search text changes."""
        self._populate_tree()
    
    def _clear_search(self):
        """Clear search text."""
        self.search_var.set("")
    
    def _sort_by_column(self, col, reverse):
        """Sort treeview by column."""
        try:
            # Get all items
            items = [(self.tree.set(item, col), item) for item in self.tree.get_children("")]
            
            # Sort items
            items.sort(reverse=reverse)
            
            # Rearrange items in sorted positions
            for index, (val, item) in enumerate(items):
                self.tree.move(item, "", index)
            
            # Reverse sort next time
            self.tree.heading(col, command=lambda: self._sort_by_column(col, not reverse))
        except Exception as e:
            self.logger.debug(f"Sort error: {e}")
    
    def _export_to_text(self):
        """Export tags to text file."""
        if not self.all_tags:
            messagebox.showwarning("Tag Viewer", "No tags to export")
            return
        
        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
                title="Export Tags to Text"
            )
            
            if not filepath:
                return
            
            # Format tags
            include_private = self.show_private_var.get()
            text = format_tag_list(self.all_tags, include_private=include_private)
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(text)
            
            messagebox.showinfo("Tag Viewer", f"Tags exported to:\n{filepath}")
            self.logger.info(f"Exported tags to: {filepath}")
        
        except Exception as e:
            error_msg = f"Failed to export tags: {e}"
            messagebox.showerror("Tag Viewer Error", error_msg)
            self.logger.exception("Failed to export tags")
    
    def _show_statistics(self):
        """Show tag statistics."""
        if not self.all_tags:
            messagebox.showwarning("Tag Viewer", "No tags loaded")
            return
        
        try:
            stats = get_tag_statistics(self.all_tags)
            
            # Format VR counts
            vr_list = []
            for vr, count in sorted(stats['vr_counts'].items(), key=lambda x: x[1], reverse=True):
                vr_list.append(f"  {vr}: {count}")
            vr_summary = "\n".join(vr_list[:10])  # Top 10
            if len(stats['vr_counts']) > 10:
                vr_summary += f"\n  ... and {len(stats['vr_counts']) - 10} more"
            
            msg = "Tag Statistics\n"
            msg += "=" * 39 + "\n\n"
            msg += f"Total Tags: {stats['total']}\n"
            msg += f"Public Tags: {stats['public']}\n"
            msg += f"Private Tags: {stats['private']}\n\n"
            msg += "Top Value Representations:\n"
            msg += vr_summary
            
            messagebox.showinfo("Tag Statistics", msg)
        
        except Exception as e:
            messagebox.showerror("Tag Viewer Error", f"Failed to generate statistics: {e}")
            self.logger.exception("Failed to generate tag statistics")


def show_tag_viewer(parent, logger, filepath=None, dataset=None):
    """
    Show tag viewer dialog.
    
    Args:
        parent: Parent window
        logger: Logger instance
        filepath: Optional path to DICOM file
        dataset: Optional pydicom Dataset
        
    Returns:
        TagViewerDialog instance
    """
    dialog = TagViewerDialog(parent, logger, filepath=filepath, dataset=dataset)
    return dialog
