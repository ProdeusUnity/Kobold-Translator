import tkinter as tk
from tkinter import ttk, messagebox
import json
import requests
import keyboard
from threading import Thread
import pyperclip

class TranslationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("KoboldAI Translator")
        self.root.geometry("600x400")
        
        # API Configuration
        self.api_url = "http://localhost:5001"  # Default KoboldAI endpoint
        self.model_info = self.get_model_info()
        
        # Languages
        self.languages = [
            "English", "Spanish", "French", "German", "Italian", 
            "Portuguese", "Russian", "Japanese", "Chinese", "Korean",
            "Arabic", "Hindi", "Dutch", "Greek", "Turkish"
        ]
        
        self.setup_ui()
        self.setup_hotkey()
        
    def setup_ui(self):
        # Model Info Display
        model_frame = ttk.LabelFrame(self.root, text="Model Information", padding=10)
        model_frame.pack(fill="x", padx=10, pady=5)
        
        model_label = ttk.Label(model_frame, text=f"Current Model: {self.model_info}")
        model_label.pack()
        
        # Translation Frame
        translation_frame = ttk.Frame(self.root, padding=10)
        translation_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Source Language
        source_frame = ttk.LabelFrame(translation_frame, text="Source Language", padding=5)
        source_frame.pack(fill="x", pady=5)
        
        self.source_lang = ttk.Combobox(source_frame, values=self.languages)
        self.source_lang.set("English")
        self.source_lang.pack(fill="x")
        
        # Target Language
        target_frame = ttk.LabelFrame(translation_frame, text="Target Language", padding=5)
        target_frame.pack(fill="x", pady=5)
        
        self.target_lang = ttk.Combobox(target_frame, values=self.languages)
        self.target_lang.set("Spanish")
        self.target_lang.pack(fill="x")
        
        # Input Text
        input_frame = ttk.LabelFrame(translation_frame, text="Input Text", padding=5)
        input_frame.pack(fill="both", expand=True, pady=5)
        
        self.input_text = tk.Text(input_frame, height=5)
        self.input_text.pack(fill="both", expand=True)
        
        # Output Text
        output_frame = ttk.LabelFrame(translation_frame, text="Translation", padding=5)
        output_frame.pack(fill="both", expand=True, pady=5)
        
        self.output_text = tk.Text(output_frame, height=5)
        self.output_text.pack(fill="both", expand=True)
        
        # Buttons
        button_frame = ttk.Frame(translation_frame)
        button_frame.pack(fill="x", pady=5)
        
        translate_btn = ttk.Button(button_frame, text="Translate", command=self.translate)
        translate_btn.pack(side="left", padx=5)
        
        clear_btn = ttk.Button(button_frame, text="Clear", command=self.clear_fields)
        clear_btn.pack(side="left", padx=5)
        
        copy_btn = ttk.Button(button_frame, text="Copy Translation", command=self.copy_translation)
        copy_btn.pack(side="left", padx=5)
        
    def setup_hotkey(self):
        # Setup global hotkey (Ctrl+Shift+T)
        keyboard.add_hotkey('ctrl+shift+k', self.show_quick_translate)
        
    def get_model_info(self):
        try:
            response = requests.post(f"{self.api_url}/api/v1/model", 
                                  headers={'Content-Type': 'application/json'})
            if response.ok:
                return response.json().get('result', 'Unknown')
            return "Could not fetch model info"
        except:
            return "Connection Error"
            
    def translate(self):
        source = self.source_lang.get()
        target = self.target_lang.get()
        text = self.input_text.get("1.0", "end-1c")
        
        if not text.strip():
            messagebox.showwarning("Warning", "Please enter text to translate")
            return
            
        prompt = f"Input: {text} ({source})\nOutput: ({target})"
        
        try:
            response = requests.post(
                f"{self.api_url}/api/v1/generate",
                json={
                    "prompt": prompt,
                    "max_length": 50,
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            )
            
            if response.ok:
                result = response.json()
                translation = result.get('results', [{}])[0].get('text', '').strip()
                self.output_text.delete("1.0", "end")
                self.output_text.insert("1.0", translation)
            else:
                messagebox.showerror("Error", "Translation failed")
                
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")
            
    def clear_fields(self):
        self.input_text.delete("1.0", "end")
        self.output_text.delete("1.0", "end")
        
    def copy_translation(self):
        translation = self.output_text.get("1.0", "end-1c")
        pyperclip.copy(translation)
        messagebox.showinfo("Success", "Translation copied to clipboard")
        
    def show_quick_translate(self):
        quick_window = tk.Toplevel(self.root)
        quick_window.title("Quick Translate")
        quick_window.geometry("400x200")
        
        # Get clipboard content
        clipboard_text = pyperclip.paste()
        
        input_frame = ttk.LabelFrame(quick_window, text="Text to Translate", padding=5)
        input_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        quick_input = tk.Text(input_frame, height=3)
        quick_input.pack(fill="both", expand=True)
        quick_input.insert("1.0", clipboard_text)
        
        button_frame = ttk.Frame(quick_window, padding=5)
        button_frame.pack(fill="x", padx=10)
        
        def quick_translate():
            text = quick_input.get("1.0", "end-1c")
            self.input_text.delete("1.0", "end")
            self.input_text.insert("1.0", text)
            self.translate()
            quick_window.destroy()
            
        translate_btn = ttk.Button(button_frame, text="Translate", command=quick_translate)
        translate_btn.pack(side="left", padx=5)
        
        cancel_btn = ttk.Button(button_frame, text="Cancel", 
                              command=quick_window.destroy)
        cancel_btn.pack(side="left", padx=5)

def main():
    root = tk.Tk()
    app = TranslationApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()