import Foundation
import PDFKit
import AppKit
let args = CommandLine.arguments
let url = URL(fileURLWithPath: args[1]); let outDir = args[2]; let scale = CGFloat(Double(args.count > 3 ? args[3] : "1.4") ?? 1.4)
guard let doc = PDFDocument(url: url) else { print("cannot open"); exit(1) }
print("pages:", doc.pageCount)
for i in 0..<doc.pageCount {
  guard let page = doc.page(at: i) else { continue }
  let rect = page.bounds(for: .mediaBox)
  let w = Int(rect.width * scale), h = Int(rect.height * scale)
  let img = NSImage(size: NSSize(width: w, height: h))
  img.lockFocus()
  NSColor.white.set(); NSRect(x: 0, y: 0, width: w, height: h).fill()
  let ctx = NSGraphicsContext.current!.cgContext
  ctx.scaleBy(x: scale, y: scale)
  page.draw(with: .mediaBox, to: ctx)
  img.unlockFocus()
  let rep = NSBitmapImageRep(data: img.tiffRepresentation!)!
  let png = rep.representation(using: .png, properties: [:])!
  try! png.write(to: URL(fileURLWithPath: String(format: "%@/p%02d.png", outDir, i + 1)))
}
