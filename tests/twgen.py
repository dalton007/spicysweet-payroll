"""
Generate just enough Tailwind-equivalent CSS for the classes this app uses,
so the server-rendered views can be screenshotted without the CDN.
Unhandled tokens are reported so gaps are visible.
"""
import re, sys, json

PALETTE = {
 'pink':   {50:'#FFF7FB',100:'#FFEAF4',200:'#FFD0E6',300:'#FFA8CF',400:'#F96FB0',500:'#F04393',600:'#EC2A86',700:'#C2156B',800:'#951050',900:'#6B0B3A'},
 'rose':   {50:'#FFF5F6',100:'#FFE4E7',200:'#FFC6CC',300:'#FF99A4',400:'#F65E70',500:'#E73A4E',600:'#DE2A3C',700:'#B21A2A',800:'#8A1420',900:'#5E0D16'},
 'red':    {50:'#FFF5F6',100:'#FFE3E6',200:'#FFC4CA',300:'#FF949F',400:'#F75C6E',500:'#E53348',600:'#DE2A3C',700:'#A8101F',800:'#850C18',900:'#5C0810'},
 'slate':  {50:'#FAF7FB',100:'#F4EEF6',200:'#E7DEEB',300:'#D1C4D8',400:'#A092A8',500:'#7D6D86',600:'#5F5069',700:'#473A50',800:'#2F2438',900:'#1C1126'},
 'yellow': {50:'#FFFCEC',100:'#FDF3D2',200:'#F9E6A3',300:'#F4D86F',400:'#EFC838',500:'#DDB220',600:'#B98E16',700:'#8E6B12',800:'#6B5010',900:'#4A370B'},
 'amber':  {50:'#FFFBEB',100:'#FDF3D2',200:'#F9E6A3',300:'#F4D86F',400:'#EFC838',500:'#DDB220',600:'#B98E16',700:'#8E6B12',800:'#6B5010',900:'#4A370B'},
 'sky':    {50:'#F2FBFE',100:'#E0F5FC',200:'#C2EBF8',300:'#9FDCF2',400:'#6AC6E6',500:'#38A9D1',600:'#2287AE',700:'#1A6A8A',800:'#15516A',900:'#0F3A4C'},
 'emerald':{50:'#F0FBF6',100:'#D7F4E7',200:'#AAE7CD',300:'#6FD3AB',400:'#38B88A',500:'#1E9E73',600:'#16815E',700:'#13674C',800:'#10503C',900:'#0B382A'},
 'white': '#ffffff', 'black': '#000000', 'transparent': 'transparent',
}
SP = {'0':'0','0.5':'.125rem','1':'.25rem','1.5':'.375rem','2':'.5rem','2.5':'.625rem','3':'.75rem','3.5':'.875rem',
      '4':'1rem','5':'1.25rem','6':'1.5rem','7':'1.75rem','8':'2rem','9':'2.25rem','10':'2.5rem','11':'2.75rem','12':'3rem',
      '14':'3.5rem','16':'4rem','20':'5rem','24':'6rem','28':'7rem','32':'8rem','36':'9rem','40':'10rem','44':'11rem','48':'12rem',
      '56':'14rem','64':'16rem','px':'1px','auto':'auto','full':'100%','screen':'100vh'}
TEXT = {'xs':('.75rem','1rem'),'sm':('.875rem','1.25rem'),'base':('1rem','1.5rem'),'lg':('1.125rem','1.75rem'),
        'xl':('1.25rem','1.75rem'),'2xl':('1.5rem','2rem'),'3xl':('1.875rem','2.25rem'),'4xl':('2.25rem','2.5rem')}
WEIGHT = {'normal':'400','medium':'500','semibold':'600','bold':'700','extrabold':'800','black':'900'}
RADIUS = {'':'.25rem','sm':'.125rem','md':'9px','lg':'13px','xl':'18px','2xl':'24px','3xl':'1.5rem','full':'9999px','none':'0'}
SHADOW = {'sm':'0 1px 2px 0 rgb(0 0 0 / .05)','':'0 1px 3px 0 rgb(0 0 0 / .1), 0 1px 2px -1px rgb(0 0 0 / .1)',
          'md':'0 4px 6px -1px rgb(0 0 0 / .1), 0 2px 4px -2px rgb(0 0 0 / .1)','lg':'0 10px 15px -3px rgb(0 0 0 / .1), 0 4px 6px -4px rgb(0 0 0 / .1)',
          'xl':'0 20px 25px -5px rgb(0 0 0 / .1), 0 8px 10px -6px rgb(0 0 0 / .1)','none':'none'}
MAXW = {'xs':'20rem','sm':'24rem','md':'28rem','lg':'32rem','xl':'36rem','2xl':'42rem','3xl':'48rem','4xl':'56rem','5xl':'64rem','6xl':'72rem','7xl':'80rem','full':'100%','none':'none'}
TRACK = {'tighter':'-.05em','tight':'-.025em','normal':'0','wide':'.025em','wider':'.05em','widest':'.1em'}
LEAD = {'none':'1','tight':'1.25','snug':'1.375','normal':'1.5','relaxed':'1.625','loose':'2'}
BP = {'sm':'640px','md':'768px','lg':'1024px','xl':'1280px','2xl':'1536px'}

def color(tok):
    """'pink-600', 'white', 'slate-900/60', 'white/20' -> css color"""
    m = re.match(r'^([a-z]+)(?:-(\d{2,3}))?(?:/(\d{1,3}))?$', tok)
    if not m: return None
    name, shade, alpha = m.groups()
    base = PALETTE.get(name)
    if base is None: return None
    hexv = base if isinstance(base, str) else base.get(int(shade) if shade else 500)
    if hexv is None: return None
    if alpha is not None and hexv.startswith('#'):
        r, g, b = int(hexv[1:3],16), int(hexv[3:5],16), int(hexv[5:7],16)
        return f'rgb({r} {g} {b} / {int(alpha)/100})'
    return hexv

def arb(v):
    """[11px] -> 11px"""
    m = re.match(r'^\[(.+)\]$', v)
    return m.group(1).replace('_',' ') if m else None

def rule(cls):
    """return list of css declarations for a bare class (no variant), or None"""
    c = cls
    # display / layout
    simple = {
      'flex':'display:flex','inline-flex':'display:inline-flex','grid':'display:grid','block':'display:block',
      'inline-block':'display:inline-block','inline':'display:inline','hidden':'display:none','table':'display:table',
      'flex-col':'flex-direction:column','flex-row':'flex-direction:row','flex-wrap':'flex-wrap:wrap','flex-1':'flex:1 1 0%',
      'grow':'flex-grow:1','shrink-0':'flex-shrink:0','shrink':'flex-shrink:1',
      'items-center':'align-items:center','items-start':'align-items:flex-start','items-end':'align-items:flex-end','items-baseline':'align-items:baseline',
      'justify-between':'justify-content:space-between','justify-center':'justify-content:center','justify-end':'justify-content:flex-end','justify-start':'justify-content:flex-start',
      'relative':'position:relative','absolute':'position:absolute','fixed':'position:fixed','sticky':'position:sticky',
      'inset-0':'inset:0','top-0':'top:0','left-0':'left:0','right-0':'right:0','bottom-0':'bottom:0',
      'overflow-hidden':'overflow:hidden','overflow-x-auto':'overflow-x:auto','overflow-y-auto':'overflow-y:auto','overflow-auto':'overflow:auto',
      'truncate':'overflow:hidden;text-overflow:ellipsis;white-space:nowrap','whitespace-nowrap':'white-space:nowrap',
      'uppercase':'text-transform:uppercase','capitalize':'text-transform:capitalize','normal-case':'text-transform:none',
      'italic':'font-style:italic','underline':'text-decoration:underline','line-through':'text-decoration:line-through',
      'text-left':'text-align:left','text-center':'text-align:center','text-right':'text-align:right',
      'align-middle':'vertical-align:middle','align-top':'vertical-align:top',
      'cursor-pointer':'cursor:pointer','cursor-not-allowed':'cursor:not-allowed','select-none':'user-select:none',
      'border':'border-width:1px;border-style:solid','border-t':'border-top-width:1px;border-style:solid','border-b':'border-bottom-width:1px;border-style:solid',
      'border-dashed':'border-style:dashed','border-0':'border-width:0',
      'w-full':'width:100%','h-full':'height:100%','min-h-screen':'min-height:100vh','w-screen':'width:100vw',
      'mx-auto':'margin-left:auto;margin-right:auto','ml-auto':'margin-left:auto','mr-auto':'margin-right:auto',
      'tabular-nums':'font-variant-numeric:tabular-nums','antialiased':'-webkit-font-smoothing:antialiased',
      'backdrop-blur':'backdrop-filter:blur(8px)','drop-shadow':'filter:drop-shadow(0 1px 2px rgb(0 0 0/.1)) drop-shadow(0 1px 1px rgb(0 0 0/.06))',
      'drop-shadow-lg':'filter:drop-shadow(0 10px 8px rgb(0 0 0/.04)) drop-shadow(0 4px 3px rgb(0 0 0/.1))',
      'transition-transform':'transition:transform .15s','animate-pulse':'animation:tw-pulse 2s cubic-bezier(.4,0,.6,1) infinite',
      'leading-none':'line-height:1','leading-tight':'line-height:1.25','leading-snug':'line-height:1.375',
      'font-mono':'font-family:ui-monospace,SFMono-Regular,Menlo,monospace','font-display':'font-family:"Inter Display",Inter,sans-serif;letter-spacing:-.015em',
      'object-contain':'object-fit:contain','pointer-events-none':'pointer-events:none',
      'justify-self-end':'justify-self:end','whitespace-pre-wrap':'white-space:pre-wrap','leading-relaxed':'line-height:1.625',
      'self-end':'align-self:flex-end','self-center':'align-self:center','basis-full':'flex-basis:100%','basis-auto':'flex-basis:auto',
      'cursor-pointer':'cursor:pointer','overflow-x-auto':'overflow-x:auto','border-collapse':'border-collapse:collapse',
      'overflow-y-auto':'overflow-y:auto','opacity-40':'opacity:.4','inline-flex':'display:inline-flex',
    }
    if c in simple: return simple[c]
    # grid cols / span
    m = re.match(r'^grid-cols-(\d+)$', c)
    if m: return f'grid-template-columns:repeat({m.group(1)},minmax(0,1fr))'
    m = re.match(r'^grid-cols-\[(.+)\]$', c)
    if m: return 'grid-template-columns:' + m.group(1).replace('_', ' ')
    if c == '-translate-x-1/2': return 'transform:translateX(-50%)'
    if c == 'scroll-mt-24': return 'scroll-margin-top:6rem'
    if c.startswith('-') and c[1:]:
        inner = rule(c[1:])
        if inner: return ';'.join(re.sub(r':(\S+)$', r':-\1', d) for d in inner.split(';'))
    m = re.match(r'^col-span-(\d+)$', c)
    if m: return f'grid-column:span {m.group(1)}/span {m.group(1)}'
    # z
    m = re.match(r'^z-(\d+)$', c)
    if m: return f'z-index:{m.group(1)}'
    # spacing: p m gap space w h min/max
    m = re.match(r'^(gap-x|gap-y|p|px|py|pt|pb|pl|pr|m|mx|my|mt|mb|ml|mr|gap|w|h|top|left|right|bottom)-(-?)(.+)$', c)
    if m:
        prop, neg, val = m.groups()
        v = SP.get(val) or arb(val)
        if v is None:
            # fractions like w-1/2
            fm = re.match(r'^(\d+)/(\d+)$', val)
            if fm: v = f'{int(fm.group(1))/int(fm.group(2))*100:.4f}%'
        if v is None: return None
        if neg: v = '-' + v
        maps = {'p':'padding','px':'padding-left;padding-right','py':'padding-top;padding-bottom','pt':'padding-top','pb':'padding-bottom','pl':'padding-left','pr':'padding-right',
                'm':'margin','mx':'margin-left;margin-right','my':'margin-top;margin-bottom','mt':'margin-top','mb':'margin-bottom','ml':'margin-left','mr':'margin-right',
                'gap':'gap','gap-x':'column-gap','gap-y':'row-gap','w':'width','h':'height','top':'top','left':'left','right':'right','bottom':'bottom'}
        return ';'.join(f'{p}:{v}' for p in maps[prop].split(';'))
    m = re.match(r'^(min-w|max-w|min-h|max-h)-(.+)$', c)
    if m:
        prop, val = m.groups()
        v = MAXW.get(val) if prop=='max-w' else None
        v = v or SP.get(val) or arb(val)
        if v is None: return None
        return f'{prop.replace("-","-") }{"idth" if prop.endswith("w") else "eight"}:{v}'.replace('min-width','min-width').replace('max-width','max-width')
    m = re.match(r'^space-(x|y)-(.+)$', c)
    if m:
        axis, val = m.groups(); v = SP.get(val) or arb(val)
        if v is None: return None
        return ('>*+*{margin-top:%s}' % v) if axis=='y' else ('>*+*{margin-left:%s}' % v)
    # text size / color / weight
    m = re.match(r'^text-(.+)$', c)
    if m:
        v = m.group(1)
        if v in TEXT: return f'font-size:{TEXT[v][0]};line-height:{TEXT[v][1]}'
        a = arb(v)
        if a: return f'font-size:{a};line-height:1.35'
        col = color(v)
        if col: return f'color:{col}'
        return None
    m = re.match(r'^font-(.+)$', c)
    if m and m.group(1) in WEIGHT: return f'font-weight:{WEIGHT[m.group(1)]}'
    m = re.match(r'^tracking-(.+)$', c)
    if m and m.group(1) in TRACK: return f'letter-spacing:{TRACK[m.group(1)]}'
    m = re.match(r'^leading-(.+)$', c)
    if m and m.group(1) in LEAD: return f'line-height:{LEAD[m.group(1)]}'
    # bg / border / accent / ring colors
    m = re.match(r'^(bg|border|accent|ring|from|via|to|shadow)-(.+)$', c)
    if m:
        kind, v = m.groups()
        col = color(v)
        if kind == 'bg' and col: return f'background-color:{col}'
        if kind == 'border' and col: return f'border-color:{col}'
        if kind == 'accent' and col: return f'accent-color:{col}'
        if kind == 'ring' and col: return f'--tw-ring:{col}'
        if kind == 'shadow' and col: return f'--tw-shadow-color:{col}'
        if kind in ('from','via','to') and col: return f'--tw-{kind}:{col}'
    m = re.match(r'^bg-gradient-to-(r|b|l|t|br|bl)$', c)
    if m:
        d = {'r':'to right','b':'to bottom','l':'to left','t':'to top','br':'to bottom right','bl':'to bottom left'}[m.group(1)]
        return f'background-image:linear-gradient({d},var(--tw-from),var(--tw-via,var(--tw-from)),var(--tw-to))'
    # radius / shadow
    m = re.match(r'^rounded(?:-(.+))?$', c)
    if m:
        k = m.group(1) or ''
        if k in RADIUS: return f'border-radius:{RADIUS[k]}'
        if k.startswith('t-'): return f'border-top-left-radius:{RADIUS.get(k[2:], ".25rem")};border-top-right-radius:{RADIUS.get(k[2:], ".25rem")}'
    m = re.match(r'^shadow(?:-(sm|md|lg|xl|none))?$', c)
    if m: return f'box-shadow:{SHADOW[m.group(1) or ""]}'
    m = re.match(r'^opacity-(\d+)$', c)
    if m: return f'opacity:{int(m.group(1))/100}'
    # border widths
    m = re.match(r'^border-(\d)$', c)
    if m: return f'border-width:{m.group(1)}px;border-style:solid'
    m = re.match(r'^border-t-(\d)$', c)
    if m: return f'border-top-width:{m.group(1)}px'
    # hover scale
    if c == 'scale-105': return 'transform:scale(1.05)'
    return None

def esc(cls):
    return re.sub(r'([^a-zA-Z0-9_-])', lambda m: '\\' + m.group(1), cls)

def build(classes):
    out = ['@keyframes tw-pulse{50%{opacity:.5}}',
           '*,*::before,*::after{box-sizing:border-box;border:0 solid #e5e7eb}',
           'body{margin:0;line-height:1.5}', 'img,svg{display:block;max-width:100%}',
           'button{background:none;border:0;padding:0;font:inherit;color:inherit;cursor:pointer}',
           'input,select,textarea{font:inherit;color:inherit}', 'ul{list-style:none;margin:0;padding:0}',
           'p,h1,h2,h3,h4{margin:0}', 'table{border-collapse:collapse}']
    unhandled = set()
    for cls in sorted(classes):
        parts = cls.split(':')
        base = parts[-1]; variants = parts[:-1]
        decl = rule(base)
        if decl is None:
            if not base.startswith('ss-') and base not in ('tabular','num','font-display'):
                unhandled.add(cls)
            continue
        sel = '.' + esc(cls)
        if '>*+*{' in decl:
            inner = decl.split('{')[1].rstrip('}')
            body_sel = sel + '>*+*'
            css = f'{body_sel}{{{inner}}}'
        else:
            css = f'{sel}{{{decl}}}'
        wrap_media = None
        for v in variants:
            if v in BP: wrap_media = f'@media (min-width:{BP[v]})'
            elif v == 'hover': css = css.replace(sel, sel + ':hover', 1)
            elif v == 'focus': css = css.replace(sel, sel + ':focus', 1)
            elif v == 'disabled': css = css.replace(sel, sel + ':disabled', 1)
            elif v == 'print': wrap_media = '@media print'
        if wrap_media: css = f'{wrap_media}{{{css}}}'
        out.append(css)
    return '\n'.join(out), unhandled

def extract(jsx):
    toks = set()
    # every quoted/backticked string's whitespace-separated tokens that look like classes
    for s in re.findall(r'className=\{?["`\']([^"`\']*)["`\']', jsx):
        toks.update(t for t in s.split() if t and not t.startswith('${'))
    # template literal pieces: className={`a b ${x ? "c d" : "e"}`}
    for s in re.findall(r'className=\{`([^`]*)`\}', jsx):
        for part in re.split(r'\$\{[^}]*\}', s):
            toks.update(part.split())
        for inner in re.findall(r'"([^"]*)"', s):
            toks.update(inner.split())
    # plain string literals inside ternaries used as classes
    for s in re.findall(r'"([a-z0-9:\-\.\[\]/#%()_,\s]{1,400})"', jsx):
        for t in s.split():
            if re.match(r'^[a-z][a-z0-9:\-\./\[\]#%]*$', t) and ('-' in t or t in ('flex','grid','block','hidden','truncate','italic','border','grow','relative','absolute','fixed','sticky','uppercase','underline')):
                toks.add(t)
    return toks

if __name__ == '__main__':
    jsx = open(sys.argv[1]).read()
    classes = extract(jsx)
    css, missing = build(classes)
    open(sys.argv[2], 'w').write(css)
    print(f'{len(classes)} class tokens -> css written; {len(missing)} unhandled')
    if missing:
        print('unhandled sample:', sorted(missing)[:60])
