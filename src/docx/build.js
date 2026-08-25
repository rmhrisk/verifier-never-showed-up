const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, PageBreak,
  Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType, ImageRun,
  PageOrientation, Header, Footer, PageNumber, TableOfContents, convertInchesToTwip
} = require('docx');

const D = __dirname;
const content = JSON.parse(fs.readFileSync(path.join(D, 'content.json'), 'utf8'));
const record  = JSON.parse(fs.readFileSync(path.join(D, 'record.json'), 'utf8'));
const diag    = JSON.parse(fs.readFileSync(path.join(D, 'diagnostic.json'), 'utf8'));
const sources = JSON.parse(fs.readFileSync(path.join(D, 'sources.json'), 'utf8'));
const strip   = JSON.parse(fs.readFileSync(path.join(D, 'artifacts.json'), 'utf8'));

const SERIF = 'Georgia', SANS = 'Segoe UI';
const INK = '16181D', MUTED = '6A6F79', RULE = 'C6C6BD', ACCENT = '1F4E5F';

const img = (rel, wIn) => {
  const p = path.join(D, rel);
  if (!fs.existsSync(p)) return null;
  const buf = fs.readFileSync(p);
  const type = rel.endsWith('.jpg') ? 'jpg' : 'png';
  // preserve aspect from the raster
  const dims = type === 'png' ? pngSize(buf) : jpgSize(buf);
  const w = wIn * 96, h = dims ? Math.round(w * dims.h / dims.w) : Math.round(w * 0.5);
  return new Paragraph({
    alignment: AlignmentType.CENTER, spacing: { before: 200, after: 60 },
    children: [new ImageRun({ type, data: buf, transformation: { width: Math.round(w), height: h } })]
  });
};
function pngSize(b){ return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) }; }
function jpgSize(b){
  let i = 2;
  while (i < b.length) {
    if (b[i] !== 0xFF) { i++; continue; }
    const m = b[i+1];
    if (m >= 0xC0 && m <= 0xCF && m !== 0xC4 && m !== 0xC8 && m !== 0xCC)
      return { h: b.readUInt16BE(i+5), w: b.readUInt16BE(i+7) };
    i += 2 + b.readUInt16BE(i+2);
  }
  return null;
}

const body = (text, opts = {}) => new Paragraph({
  spacing: { after: 160, line: 300 },
  alignment: opts.align || AlignmentType.LEFT,
  children: [new TextRun({ text, font: SERIF, size: 21, color: INK, italics: !!opts.italics })]
});
const small = (text, opts = {}) => new Paragraph({
  spacing: { after: opts.after ?? 120 },
  alignment: opts.align || AlignmentType.LEFT,
  children: [new TextRun({ text, font: SANS, size: 16, color: opts.color || MUTED, italics: !!opts.italics })]
});
const rule = () => new Paragraph({
  spacing: { before: 120, after: 160 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: RULE } }, children: []
});

const kids = [];

/* ---------- cover ---------- */
kids.push(new Paragraph({ spacing: { before: 1800, after: 240 }, children: [
  new TextRun({ text: 'The Verifier Never Showed Up', font: SERIF, size: 60, color: INK })]}));
const sf = content.find(b => b.t === 'standfirst');
if (sf) kids.push(new Paragraph({ spacing: { after: 420 }, children: [
  new TextRun({ text: sf.v, font: SERIF, size: 26, color: '3A3E47' })]}));
const by = content.find(b => b.t === 'byline');
kids.push(rule());
if (by) kids.push(small(by.v.toUpperCase(), { color: INK, after: 60 }));
content.filter(b => b.t === 'snapshot').forEach(b => kids.push(small(b.v, { italics: true, after: 100 })));
kids.push(new Paragraph({ children: [new PageBreak()] }));

/* ---------- contents ---------- */
kids.push(new Paragraph({ spacing: { after: 200 }, children: [
  new TextRun({ text: 'Contents', font: SANS, size: 28, bold: true, color: INK })]}));
kids.push(new TableOfContents('Contents', { hyperlink: true, headingStyleRange: '1-2' }));
kids.push(new Paragraph({ children: [new PageBreak()] }));

/* ---------- body ---------- */
let figCount = 0;
for (const b of content) {
  switch (b.t) {
    case 'title': case 'standfirst': case 'byline': case 'snapshot':
      break;
    case 'part':
      kids.push(new Paragraph({ children: [new PageBreak()] }));
      kids.push(new Paragraph({ spacing: { before: 1200, after: 80 }, children: [
        new TextRun({ text: b.eyebrow.toUpperCase(), font: SANS, size: 18, bold: true, color: ACCENT })]}));
      kids.push(new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { after: 400 }, children: [
        new TextRun({ text: b.title, font: SERIF, size: 44, color: INK })]}));
      break;
    case 'h3':
      kids.push(new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 400, after: 160 }, children: [
        new TextRun({ text: (b.n ? b.n + '.  ' : '') + b.v, font: SERIF, size: 30, color: INK })]}));
      break;
    case 'h4':
      kids.push(new Paragraph({ heading: HeadingLevel.HEADING_3, spacing: { before: 280, after: 120 }, children: [
        new TextRun({ text: b.v, font: SANS, size: 21, bold: true, color: INK })]}));
      break;
    case 'thesis':
      kids.push(new Paragraph({ spacing: { before: 200, after: 140 },
        border: { top: { style: BorderStyle.SINGLE, size: 8, color: INK } },
        children: [new TextRun({ text: 'THE ARGUMENT IN FIVE CLAIMS', font: SANS, size: 17, bold: true, color: MUTED })] }));
      b.items.forEach((it, i) => {
        kids.push(new Paragraph({ spacing: { after: 40 }, children: [
          new TextRun({ text: (i + 1) + '.  ', font: SANS, size: 19, color: ACCENT }),
          new TextRun({ text: it.claim, font: SERIF, size: 21, color: INK })]}));
        kids.push(small('     ' + it.refs, { after: 140 }));
      });
      kids.push(rule());
      break;
    case 'quote':
      kids.push(new Paragraph({
        spacing: { before: 200, after: 200 }, indent: { left: convertInchesToTwip(0.4) },
        border: { left: { style: BorderStyle.SINGLE, size: 12, color: ACCENT, space: 12 } },
        children: [new TextRun({ text: b.v, font: SERIF, size: 23, italics: true, color: INK })] }));
      break;
    case 'lesson':
      kids.push(new Paragraph({
        spacing: { before: 200, after: 60 }, shading: { type: ShadingType.CLEAR, fill: 'F3F3EF' },
        children: [new TextRun({ text: 'KEY LESSON', font: SANS, size: 16, bold: true, color: MUTED })] }));
      kids.push(new Paragraph({
        spacing: { after: 220 }, shading: { type: ShadingType.CLEAR, fill: 'F3F3EF' },
        children: [new TextRun({ text: b.v, font: SANS, size: 19, color: INK })] }));
      break;
    case 'skip': break;
    case 'strip': {
      // four artifacts as one row, each with its own caption and failure line
      const W = [2400, 2400, 2400, 2400];
      const cells = strip.items.map((a, i) => {
        const p = path.join(D, `figs/photo${i}.jpg`);
        const buf = fs.readFileSync(p); const d = jpgSize(buf);
        const w = 150, hh = Math.round(w * d.h / d.w);
        return new TableCell({
          width: { size: W[i], type: WidthType.DXA },
          margins: { top: 80, bottom: 80, left: 80, right: 80 },
          borders: { top:{style:BorderStyle.NONE}, bottom:{style:BorderStyle.NONE},
                     left:{style:BorderStyle.NONE}, right:{style:BorderStyle.NONE} },
          children: [
            new Paragraph({ alignment: AlignmentType.CENTER, spacing:{after:80}, children: [
              new ImageRun({ type:'jpg', data: buf, transformation: { width: w, height: hh } })]}),
            new Paragraph({ spacing:{after:20}, children:[new TextRun({ text:a.name, font:SANS, size:15, bold:true, color:INK })]}),
            new Paragraph({ spacing:{after:20}, children:[new TextRun({ text:a.desc, font:SANS, size:13, color:'3A3E47' })]}),
            new Paragraph({ spacing:{after:40}, children:[new TextRun({ text:a.src, font:SANS, size:12, color:MUTED })]}),
            new Paragraph({ children:[new TextRun({ text:a.fail, font:SANS, size:13, color:'B4472E' })]})
          ]});
      });
      kids.push(new Table({ columnWidths: W, width: { size: 9600, type: WidthType.DXA },
        borders: { top:{style:BorderStyle.SINGLE,size:4,color:RULE}, bottom:{style:BorderStyle.SINGLE,size:4,color:RULE},
                   left:{style:BorderStyle.NONE}, right:{style:BorderStyle.NONE},
                   insideHorizontal:{style:BorderStyle.NONE}, insideVertical:{style:BorderStyle.NONE} },
        rows: [new TableRow({ children: cells })] }));
      if (strip.cap) kids.push(small(strip.cap, { after: 240 }));
      figCount++;
      break;
    }
    case 'figure': case 'photo': {
      const p = img(b.img, b.t === 'photo' ? 4.6 : 6.2);
      if (p) { kids.push(p); figCount++; if (b.cap) kids.push(small(b.cap, { after: 220 })); }
      break;
    }
    case 'record': kids.push(new Paragraph({ children: [] })); break;   // rendered below as its own section
    case 'scorecard': kids.push(new Paragraph({ children: [] })); break;
    case 'p': kids.push(body(b.v)); break;
  }
}

/* ---------- the record, as a real table ---------- */
kids.push(new Paragraph({ children: [new PageBreak()] }));
kids.push(new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { after: 120 }, children: [
  new TextRun({ text: 'Appendix A — The Record', font: SERIF, size: 40, color: INK })]}));
const decidedN = record.filter(r => r.o !== 'In flight' && r.o !== 'Uncertain').length;
const workedN = record.filter(r => r.o === 'Working').length;
kids.push(small(record.length + ' programs, 1999 to 2024. Solid entries are primary causes; entries marked contributing are secondary. ' +
  'Of the ' + decidedN + ' where an outcome could be identified, ' + workedN + ' worked. ' +
  'In this sample, weak cryptography was not identified as the primary cause of any failed outcome.',
  { after: 240 }));

const COLS = [2100, 1250, 700, 2600, 3150];
const cell = (text, o = {}) => new TableCell({
  width: { size: o.w, type: WidthType.DXA },
  shading: o.fill ? { type: ShadingType.CLEAR, fill: o.fill } : undefined,
  margins: { top: 60, bottom: 60, left: 80, right: 80 },
  children: [new Paragraph({ children: [new TextRun({
    text, font: SANS, size: o.size || 15, bold: !!o.bold, color: o.color || INK })] })]
});
const headRow = new TableRow({ tableHeader: true, children:
  ['Program', 'Where', 'From', 'Failure modes', 'What happened'].map((t, i) =>
    cell(t, { w: COLS[i], bold: true, size: 14, fill: 'F3F3EF' })) });
const rows = [headRow].concat(record.map(r => new TableRow({ children: [
  cell(r.p, { w: COLS[0], bold: true }),
  cell(r.w, { w: COLS[1] }),
  cell(r.y, { w: COLS[2] }),
  cell(r.o + (r.tags.length ? ' · ' + r.tags.join('; ') : ''), { w: COLS[3], color: r.o === 'Failed' ? 'B4472E' : '3A3E47' }),
  cell(r.n, { w: COLS[4], size: 14, color: '3A3E47' })] })));
kids.push(new Table({
  columnWidths: COLS, width: { size: COLS.reduce((a, b) => a + b, 0), type: WidthType.DXA },
  borders: {
    top:    { style: BorderStyle.SINGLE, size: 4, color: RULE },
    bottom: { style: BorderStyle.SINGLE, size: 4, color: RULE },
    left:   { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE },
    insideHorizontal: { style: BorderStyle.SINGLE, size: 2, color: 'E4E4DE' },
    insideVertical:   { style: BorderStyle.NONE } },
  rows }));

/* ---------- the diagnostic ---------- */
kids.push(new Paragraph({ children: [new PageBreak()] }));
kids.push(new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { after: 120 }, children: [
  new TextRun({ text: 'Appendix B — Reading a Proposal', font: SERIF, size: 40, color: INK })]}));
kids.push(small('Twenty questions mapped to the eleven failure modes. Every answer that describes the weaker case is a mode the ' +
  'proposal is exposed to. Five of the eleven are structural and no delivery plan reaches them.', { after: 240 }));
diag.forEach((q, i) => {
  kids.push(new Paragraph({ spacing: { before: 140, after: 30 }, children: [
    new TextRun({ text: (i + 1) + '.  ', font: SANS, size: 19, color: ACCENT }),
    new TextRun({ text: q.q, font: SANS, size: 19, bold: true, color: INK })] }));
  kids.push(small('     ' + q.s, { after: 60 }));
});

/* ---------- sources ---------- */
kids.push(new Paragraph({ children: [new PageBreak()] }));
kids.push(new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { after: 200 }, children: [
  new TextRun({ text: 'Sources', font: SERIF, size: 40, color: INK })]}));
sources.forEach((s, i) => kids.push(new Paragraph({ spacing: { after: 120 }, children: [
  new TextRun({ text: (i + 1) + '.  ', font: SANS, size: 16, color: ACCENT }),
  new TextRun({ text: s, font: SANS, size: 16, color: '3A3E47' })] })));

/* ---------- assemble ---------- */
const doc = new Document({
  creator: 'Ryan Hurst', title: 'The Verifier Never Showed Up',
  description: 'Thirty years of digital identity programs, sorted by how they actually failed.',
  styles: { default: { document: { run: { font: SERIF, size: 21, color: INK } } } },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: {
      top: 1440, bottom: 1440, left: 1440, right: 1440 } } },
    headers: { default: new Header({ children: [new Paragraph({
      spacing: { after: 200 },
      border: { bottom: { style: BorderStyle.SINGLE, size: 3, color: RULE } },
      children: [new TextRun({ text: 'THE VERIFIER NEVER SHOWED UP', font: SANS, size: 14, color: MUTED })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ children: [PageNumber.CURRENT], font: SANS, size: 15, color: MUTED })] })] }) },
    children: kids
  }]
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(path.join(D, '..', '..', 'verifier-never-showed-up.docx'), buf);
  console.log('written | blocks', content.length, '| figures', figCount, '| record', record.length,
              '| questions', diag.length, '| sources', sources.length);
});
