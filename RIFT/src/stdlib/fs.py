"""
RIFT Standard Library - File System Module

File system operations for reading, writing, and managing files.
"""

import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional


def create_fs_module(interpreter) -> Dict[str, Any]:
    """Create the file system module for RIFT."""
    
    def fs_read(path: str, encoding: str = 'utf-8') -> str:
        """Read file contents."""
        try:
            with open(path, 'r', encoding=encoding) as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {path}")
        except IOError as e:
            raise IOError(f"Error reading file: {e}")
    
    def fs_read_bytes(path: str) -> bytes:
        """Read file as bytes."""
        try:
            with open(path, 'rb') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {path}")
        except IOError as e:
            raise IOError(f"Error reading file: {e}")
    
    def fs_write(path: str, data: str, encoding: str = 'utf-8') -> None:
        """Write data to file."""
        try:
            with open(path, 'w', encoding=encoding) as f:
                f.write(data)
        except IOError as e:
            raise IOError(f"Error writing file: {e}")
    
    def fs_write_bytes(path: str, data: bytes) -> None:
        """Write bytes to file."""
        try:
            with open(path, 'wb') as f:
                f.write(data)
        except IOError as e:
            raise IOError(f"Error writing file: {e}")
    
    def fs_append(path: str, data: str, encoding: str = 'utf-8') -> None:
        """Append data to file."""
        try:
            with open(path, 'a', encoding=encoding) as f:
                f.write(data)
        except IOError as e:
            raise IOError(f"Error appending to file: {e}")
    
    def fs_delete(path: str) -> None:
        """Delete a file."""
        try:
            os.remove(path)
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {path}")
        except OSError as e:
            raise OSError(f"Error deleting file: {e}")
    
    def fs_exists(path: str) -> bool:
        """Check if path exists."""
        return os.path.exists(path)
    
    def fs_is_file(path: str) -> bool:
        """Check if path is a file."""
        return os.path.isfile(path)
    
    def fs_is_dir(path: str) -> bool:
        """Check if path is a directory."""
        return os.path.isdir(path)
    
    def fs_mkdir(path: str, recursive: bool = True) -> None:
        """Create directory."""
        try:
            if recursive:
                os.makedirs(path, exist_ok=True)
            else:
                os.mkdir(path)
        except OSError as e:
            raise OSError(f"Error creating directory: {e}")
    
    def fs_rmdir(path: str, recursive: bool = False) -> None:
        """Remove directory."""
        try:
            if recursive:
                shutil.rmtree(path)
            else:
                os.rmdir(path)
        except FileNotFoundError:
            raise FileNotFoundError(f"Directory not found: {path}")
        except OSError as e:
            raise OSError(f"Error removing directory: {e}")
    
    def fs_list(path: str = '.') -> List[str]:
        """List directory contents."""
        try:
            return os.listdir(path)
        except FileNotFoundError:
            raise FileNotFoundError(f"Directory not found: {path}")
        except OSError as e:
            raise OSError(f"Error listing directory: {e}")
    
    def fs_stat(path: str) -> Dict[str, Any]:
        """Get file statistics."""
        try:
            stat = os.stat(path)
            return {
                'size': stat.st_size,
                'mode': stat.st_mode,
                'created': stat.st_ctime,
                'modified': stat.st_mtime,
                'accessed': stat.st_atime,
                'isFile': os.path.isfile(path),
                'isDir': os.path.isdir(path),
            }
        except FileNotFoundError:
            raise FileNotFoundError(f"Path not found: {path}")
        except OSError as e:
            raise OSError(f"Error getting file stats: {e}")
    
    def fs_copy(src: str, dest: str) -> None:
        """Copy file or directory."""
        try:
            if os.path.isdir(src):
                shutil.copytree(src, dest)
            else:
                shutil.copy2(src, dest)
        except FileNotFoundError:
            raise FileNotFoundError(f"Source not found: {src}")
        except OSError as e:
            raise OSError(f"Error copying: {e}")
    
    def fs_move(src: str, dest: str) -> None:
        """Move file or directory."""
        try:
            shutil.move(src, dest)
        except FileNotFoundError:
            raise FileNotFoundError(f"Source not found: {src}")
        except OSError as e:
            raise OSError(f"Error moving: {e}")
    
    def fs_rename(old_path: str, new_path: str) -> None:
        """Rename file or directory."""
        try:
            os.rename(old_path, new_path)
        except FileNotFoundError:
            raise FileNotFoundError(f"Path not found: {old_path}")
        except OSError as e:
            raise OSError(f"Error renaming: {e}")
    
    def fs_watch(path: str, callback) -> None:
        """Watch for file changes (basic implementation)."""
        # Note: Full implementation would use watchdog library
        # This is a simplified polling-based version
        import time
        
        last_mtime = os.path.getmtime(path) if os.path.exists(path) else 0
        
        while True:
            try:
                current_mtime = os.path.getmtime(path)
                if current_mtime != last_mtime:
                    last_mtime = current_mtime
                    callback({'path': path, 'event': 'modified'})
                time.sleep(1)
            except KeyboardInterrupt:
                break
            except FileNotFoundError:
                callback({'path': path, 'event': 'deleted'})
                break
    
    # Path utilities
    def fs_join(*parts) -> str:
        """Join path components."""
        return os.path.join(*parts)
    
    def fs_dirname(path: str) -> str:
        """Get directory name."""
        return os.path.dirname(path)
    
    def fs_basename(path: str) -> str:
        """Get base name."""
        return os.path.basename(path)
    
    def fs_extname(path: str) -> str:
        """Get file extension."""
        return os.path.splitext(path)[1]
    
    def fs_resolve(path: str) -> str:
        """Get absolute path."""
        return os.path.abspath(path)
    
    def fs_relative(path: str, base: str = None) -> str:
        """Get relative path."""
        if base is None:
            base = os.getcwd()
        return os.path.relpath(path, base)
    
    def fs_cwd() -> str:
        """Get current working directory."""
        return os.getcwd()
    
    def fs_chdir(path: str) -> None:
        """Change working directory."""
        os.chdir(path)
    
    def fs_glob(pattern: str, path: str = '.') -> List[str]:
        """Find files matching pattern."""
        import glob
        return glob.glob(os.path.join(path, pattern))
    
    return {
        'read': fs_read,
        'readBytes': fs_read_bytes,
        'write': fs_write,
        'writeBytes': fs_write_bytes,
        'append': fs_append,
        'delete': fs_delete,
        'exists': fs_exists,
        'isFile': fs_is_file,
        'isDir': fs_is_dir,
        'mkdir': fs_mkdir,
        'rmdir': fs_rmdir,
        'list': fs_list,
        'stat': fs_stat,
        'copy': fs_copy,
        'move': fs_move,
        'rename': fs_rename,
        'watch': fs_watch,
        'join': fs_join,
        'dirname': fs_dirname,
        'basename': fs_basename,
        'extname': fs_extname,
        'resolve': fs_resolve,
        'relative': fs_relative,
        'cwd': fs_cwd,
        'chdir': fs_chdir,
        'glob': fs_glob,
    }
