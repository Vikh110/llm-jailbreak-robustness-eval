-- 1) Turns fenced divs such as ::: recap ... ::: into coloured callout boxes.
-- 2) Lets long file names in inline code break across lines.
local kinds = {
  recap      = {"Chapter recap", "gblue"},
  plain      = {"In plain English", "gteal"},
  example    = {"Everyday example", "gteal"},
  documented = {"Documented reason", "gnavy"},
  interp     = {"Interpretation (not a verified fact)", "gpurple"},
  illustr    = {"Illustrative example (not project data)", "gamber"},
  proposal   = {"Proposed improvement (not done in this project)", "gamber"},
  unverified = {"Could not be verified", "gred"},
  caution    = {"Watch out", "gred"},
  project    = {"What we did in this project", "gblue"},
}

function Div(el)
  for cls, spec in pairs(kinds) do
    if el.classes:includes(cls) then
      local title = el.attributes["title"] or spec[1]
      local out = { pandoc.RawBlock("latex", "\\begin{calloutbox}{" .. title .. "}{" .. spec[2] .. "}") }
      for _, b in ipairs(el.content) do
        table.insert(out, b)
      end
      table.insert(out, pandoc.RawBlock("latex", "\\end{calloutbox}"))
      return out
    end
  end
end

-- Path-like inline code (contains / or _, no spaces or special characters) becomes \path{...},
-- which may break after / _ - . so that long file names do not run into the margin.
function Code(el)
  local t = el.text
  if #t >= 16 and t:match("[/_]") and not t:match("[^%w%._/%-]") then
    return pandoc.RawInline("latex", "{\\ttfamily\\path{" .. t .. "}}")
  end
end
