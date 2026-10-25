"""External file drops for this Tool's existing GLFW window; no extra runtime."""
import ctypes
from pathlib import Path
from queue import SimpleQueue, Empty
import sys


class FileDrops:
    def __init__(self):
        self._pending=SimpleQueue()
        self._library=None
        self._callback=None
        self._previous=None
        self.window=0
        self.native_window=0
        self.error=""

    def install(self):
        """Called after HelloImGui creates the window, on its owning thread."""
        try:
            from imgui_bundle import hello_imgui, _imgui_bundle
            window=hello_imgui.get_glfw_window_address()
            if not window:raise RuntimeError("GLFW window unavailable")
            folder=Path(_imgui_bundle.__file__).resolve().parent
            names=("glfw3.dll",) if sys.platform=="win32" else (("libglfw.3.dylib",) if sys.platform=="darwin" else ("libglfw.so.3","libglfw.3.so","libglfw.so.3.3"))
            library_path=next((folder/name for name in names if (folder/name).is_file()),None)
            if library_path is None:raise RuntimeError("Bundled GLFW library unavailable")
            library=ctypes.CDLL(str(library_path))
            library.glfwGetCurrentContext.argtypes=[]
            library.glfwGetCurrentContext.restype=ctypes.c_void_p
            if library.glfwGetCurrentContext()!=window:
                raise RuntimeError("The window does not belong to the bundled GLFW context")
            callback_type=ctypes.CFUNCTYPE(None,ctypes.c_void_p,ctypes.c_int,ctypes.POINTER(ctypes.c_char_p))
            library.glfwSetDropCallback.argtypes=[ctypes.c_void_p,ctypes.c_void_p]
            library.glfwSetDropCallback.restype=ctypes.c_void_p
            def received(native_window,count,paths):
                # The OS callback only queues UTF-8 names. File access and UI
                # changes run later on the normal application frame.
                try:
                    files=tuple(paths[i].decode("utf-8") for i in range(min(max(count,0),32)))
                    self._pending.put(files)
                except Exception:
                    self._pending.put(())
                if self._previous:
                    callback_type(self._previous)(native_window,count,paths)
            self._callback=callback_type(received)
            self._previous=library.glfwSetDropCallback(window,ctypes.cast(self._callback,ctypes.c_void_p))
            self.window=window;self._library=library
            if sys.platform=="win32":
                library.glfwGetWin32Window.argtypes=[ctypes.c_void_p]
                library.glfwGetWin32Window.restype=ctypes.c_void_p
                self.native_window=library.glfwGetWin32Window(window)
        except Exception as exc:
            self.error=str(exc)

    def poll(self):
        batches=[]
        while True:
            try:batches.append(self._pending.get_nowait())
            except Empty:return batches

    def close(self):
        """Restore the previous callback BEFORE the GLFW window is destroyed."""
        if self._library and self.window:
            self._library.glfwSetDropCallback(self.window,self._previous)
            self.window=0
