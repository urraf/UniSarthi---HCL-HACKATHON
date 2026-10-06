// Shows an answer with simple formatting: "- " / "• " lines become a bullet list and **text** becomes bold.
// Built from React elements (never raw HTML), so text from the model cannot inject markup.
function inline(text) {
  return text.split(/(\*\*[^*]+\*\*)/g).map((part, i) =>
    part.startsWith("**") && part.endsWith("**") && part.length > 4 ? <strong key={i}>{part.slice(2, -2)}</strong> : part
  );
}

export default function FormattedText({ text }) {
  const blocks = [];
  let list = null;
  for (const raw of text.split("\n")) {
    const line = raw.trim();
    const bullet = line.match(/^(?:[-•*]|\d+[.)])\s+(.*)/);
    if (bullet) {
      if (!list) {
        list = [];
        blocks.push({ type: "list", items: list });
      }
      list.push(bullet[1]);
    } else if (line) {
      list = null;
      blocks.push({ type: "p", text: line });
    }
  }
  return (
    <div className="formatted">
      {blocks.map((b, i) =>
        b.type === "list" ? (
          <ul key={i}>{b.items.map((item, j) => <li key={j}>{inline(item)}</li>)}</ul>
        ) : (
          <p key={i}>{inline(b.text)}</p>
        )
      )}
    </div>
  );
}
