const fs = require('fs');
const path = require('path');

function removeAccents(str) {
  return str.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
}

function sanitizeName(name) {
  const ext = path.extname(name);
  const base = path.basename(name, ext);
  return removeAccents(base).replace(/\s+/g, '-').toLowerCase() + ext.toLowerCase();
}

const assetsDir = path.join(__dirname, 'projects', 'uro-oncology', 'public', 'assets');
const srcDir = path.join(__dirname, 'projects', 'uro-oncology', 'src');

let replacements = [];

function walkDir(dir, callback) {
  fs.readdirSync(dir).forEach(f => {
    let dirPath = path.join(dir, f);
    let isDirectory = fs.statSync(dirPath).isDirectory();
    isDirectory ? walkDir(dirPath, callback) : callback(path.join(dir, f));
  });
}

// 1. Rename files and collect replacements
walkDir(assetsDir, (filePath) => {
  const dirName = path.dirname(filePath);
  const fileName = path.basename(filePath);
  const newFileName = sanitizeName(fileName);
  
  if (fileName !== newFileName) {
    const newFilePath = path.join(dirName, newFileName);
    fs.renameSync(filePath, newFilePath);
    
    // the reference in code would be /assets/...
    // We need to match the original filename (which could be in NFD or NFC)
    // Actually, it's safer to just replace any instance of the old name in the codebase,
    // but the original name might have been written differently in the code (NFC vs NFD).
    // So we add both.
    const oldRef1 = fileName;
    const oldRef2 = fileName.normalize("NFC");
    
    replacements.push({
      old1: oldRef1,
      old2: oldRef2,
      new: newFileName
    });
    console.log(`Renamed: ${fileName} -> ${newFileName}`);
  }
});

// 2. Update references in src
walkDir(srcDir, (filePath) => {
  if (filePath.endsWith('.js') || filePath.endsWith('.css')) {
    let content = fs.readFileSync(filePath, 'utf8');
    let originalContent = content;
    
    replacements.forEach(r => {
      // Simple string replacement
      content = content.split(r.old1).join(r.new);
      content = content.split(r.old2).join(r.new);
      
      // Also handle URL encoded spaces (%20) if any
      const encoded1 = encodeURIComponent(r.old1);
      const encoded2 = encodeURIComponent(r.old2);
      if (encoded1 !== r.old1) content = content.split(encoded1).join(r.new);
      if (encoded2 !== r.old2) content = content.split(encoded2).join(r.new);
    });
    
    if (content !== originalContent) {
      fs.writeFileSync(filePath, content, 'utf8');
      console.log(`Updated references in: ${filePath}`);
    }
  }
});
