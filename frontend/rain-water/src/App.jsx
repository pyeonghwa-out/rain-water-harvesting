import { createElement, useEffect, useMemo, useRef, useState } from 'react'
import * as THREE from 'three'
import { motion } from 'motion/react'
import { ArrowDown, ArrowRight, Check, ChevronDown, Droplets, Github, LoaderCircle, MapPin, Mountain, Ruler, Sparkles, Waves, Wind } from 'lucide-react'

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
const initialForm = { lat: '12.9715944', lon: '77.5943964', rooftop_area_m2: '', open_area_m2: '24', roof_type: 'concrete', num_persons: '4', per_capita: '35', period_days: '90' }
const money = value => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(Number(value || 0))
const number = value => new Intl.NumberFormat('en-IN', { maximumFractionDigits: 0 }).format(Number(value || 0))
const labels = { store_on_roof: 'Rainwater storage tank', recharge_on_site_pit: 'On-site recharge pit', recharge_shaft: 'Recharge shaft', recharge_well_or_injection: 'Recharge well', community_recharge_or_combination: 'Community recharge' }

function WaterScene() {
  const ref = useRef(null)
  useEffect(() => {
    const canvas = ref.current
    const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true })
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.6))
    const scene = new THREE.Scene()
    const camera = new THREE.PerspectiveCamera(36, 1, 0.1, 100)
    camera.position.z = 7
    const geometry = new THREE.IcosahedronGeometry(1.65, 3)
    const material = new THREE.MeshPhysicalMaterial({ color: 0x58d8c0, roughness: 0.17, metalness: 0.18, transparent: true, opacity: 0.78, transmission: 0.2, wireframe: false })
    const orb = new THREE.Mesh(geometry, material)
    scene.add(orb)
    const wire = new THREE.Mesh(new THREE.IcosahedronGeometry(1.68, 2), new THREE.MeshBasicMaterial({ color: 0x9affeb, wireframe: true, transparent: true, opacity: 0.17 }))
    scene.add(wire)
    scene.add(new THREE.AmbientLight(0xc8fff2, 2.1))
    const key = new THREE.PointLight(0x56ffe0, 32, 20); key.position.set(2, 3, 4); scene.add(key)
    const rim = new THREE.PointLight(0x4584ff, 18, 15); rim.position.set(-3, -2, 2); scene.add(rim)
    let frame
    const resize = () => { const { width, height } = canvas.getBoundingClientRect(); renderer.setSize(width, height, false); camera.aspect = width / Math.max(height, 1); camera.updateProjectionMatrix() }
    resize(); const observer = new ResizeObserver(resize); observer.observe(canvas)
    const tick = time => { orb.rotation.y = time * 0.00018; orb.rotation.x = Math.sin(time * 0.00022) * 0.13; wire.rotation.y = -time * 0.00012; wire.rotation.x = time * 0.00008; renderer.render(scene, camera); frame = requestAnimationFrame(tick) }
    frame = requestAnimationFrame(tick)
    return () => { cancelAnimationFrame(frame); observer.disconnect(); geometry.dispose(); material.dispose(); renderer.dispose() }
  }, [])
  return <canvas className="water-canvas" ref={ref} aria-hidden="true" />
}

function Field({ label, name, value, onChange, type = 'number', min, step = 'any', placeholder, suffix, required = true }) {
  return <label className="field"><span>{label}</span><div className="input-wrap"><input name={name} type={type} min={min} step={step} value={value} onChange={onChange} placeholder={placeholder} required={required} /><span className="unit">{suffix}</span></div></label>
}

function App() {
  void motion
  const [form, setForm] = useState(initialForm)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [health, setHealth] = useState('checking')
  const [menuOpen, setMenuOpen] = useState(false)
  const summary = useMemo(() => {
    const rainfall = Number(result?.water_balance?.rainfall_mm || result?.nearest_well_record?.mean_annual_rainfall || 0)
    return [
      { icon: Droplets, label: 'Annual harvest potential', value: `${number(result?.water_balance?.annual_harvest_l)} L`, tint: 'mint' },
      { icon: Waves, label: 'Household design demand', value: `${number(result?.water_balance?.demand_l)} L`, tint: 'blue' },
      { icon: Mountain, label: 'Local annual rainfall', value: `${number(rainfall)} mm`, tint: 'violet' },
    ]
  }, [result])

  useEffect(() => { fetch(`${API_URL}/health`).then(r => { if (!r.ok) throw new Error(); return r.json() }).then(() => setHealth('online')).catch(() => setHealth('offline')) }, [])

  const update = event => setForm(current => ({ ...current, [event.target.name]: event.target.value }))
  const submit = async event => {
    event.preventDefault(); setLoading(true); setError(''); setResult(null)
    try {
      const payload = Object.fromEntries(Object.entries(form).map(([key, value]) => [key, key === 'roof_type' ? value : key === 'rooftop_area_m2' && value === '' ? null : Number(value)]))
      const response = await fetch(`${API_URL}/predict`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
      const data = await response.json().catch(() => ({}))
      if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'Prediction failed. Check the API and submitted values.')
      setResult(data)
    } catch (err) { setError(err.message || 'Unable to connect to the prediction service.') }
    finally { setLoading(false) }
  }

  const formatKey = key => key.replaceAll('_', ' ').replace(/\b\w/g, char => char.toUpperCase())
  const dimensions = Object.entries(result?.predicted_dimensions || {})

  return <div className="app-shell">
    <header className="topbar"><a href="#top" className="brand"><span className="brand-mark"><Droplets size={19} /></span><span>ZENKAI<span className="brand-dot">.</span></span></a><button className="mobile-menu" onClick={() => setMenuOpen(!menuOpen)} aria-label="Toggle navigation"><ChevronDown size={18} /></button><nav className={menuOpen ? 'nav-links open' : 'nav-links'}><a href="#approach" onClick={() => setMenuOpen(false)}>How it works</a><a href="#predictor" onClick={() => setMenuOpen(false)}>Predictor</a><a href="#about" onClick={() => setMenuOpen(false)}>Methodology</a></nav><div className="topbar-right"><span className={`api-status ${health}`}><i />{health === 'online' ? 'API connected' : health === 'offline' ? 'API offline' : 'Connecting'}</span><a className="github-link" href="https://github.com" target="_blank" rel="noreferrer" aria-label="GitHub"><Github size={18} /></a></div></header>

    <main id="top"><section className="hero section-wrap"><div className="hero-copy"><motion.div className="eyebrow" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}><span className="eyebrow-dot" /> WATER INTELLIGENCE, REIMAGINED</motion.div><motion.h1 initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.08 }}>Make every<br /><span>drop count.</span></motion.h1><motion.p className="hero-text" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.16 }}>A smarter way to plan rainwater harvesting. Get a site-aware recommendation, practical dimensions, and a clear cost estimate in seconds.</motion.p><motion.div className="hero-actions" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.22 }}><a href="#predictor" className="button button-primary">Plan your system <ArrowRight size={17} /></a><a href="#approach" className="text-link">Explore the approach <ArrowDown size={15} /></a></motion.div><div className="hero-proof"><div className="avatar-stack"><i>R</i><i>W</i><i>+</i></div><span>Grounded in local rainfall &amp; geology data</span></div></div><div className="hero-visual"><div className="orbit orbit-one" /><div className="orbit orbit-two" /><WaterScene /><div className="visual-chip chip-top"><span className="chip-icon"><Sparkles size={15} /></span><span><b>Site-aware insights</b><small>Location + hydrogeology</small></span></div><div className="visual-chip chip-bottom"><span className="rain-bars"><i /><i /><i /><i /><i /></span><span><b>Water potential</b><small>Calculated for your roof</small></span></div><div className="visual-caption">01 <span /> RAINFALL → RESILIENCE</div></div></section>

    <section className="trust-strip section-wrap" id="approach"><div className="strip-label">A better plan starts with</div><div><MapPin /><b>Your location</b><span>Nearby observation data</span></div><div><Ruler /><b>Your property</b><span>Roof, space &amp; household</span></div><div><Wind /><b>Real constraints</b><span>Harvest &amp; recharge logic</span></div></section>

    <section className="planner section-wrap" id="predictor"><div className="section-heading"><div><div className="eyebrow"><span className="eyebrow-dot" /> THE RAINWATER PLANNER</div><h2>Find the right fit<br />for <span>your site.</span></h2></div><p>Share a few details. We’ll combine your inputs with local rainfall and groundwater observations to shape a practical recommendation.</p></div><div className="planner-grid"><motion.form className="planner-form panel" onSubmit={submit} layout><div className="form-header"><div className="step-number">01</div><div><h3>Your property details</h3><p>All fields are used to tailor your result.</p></div><span className="required-note">METRIC UNITS</span></div><div className="form-section-title">LOCATION <span>Where is your site?</span></div><div className="fields two"><Field label="Latitude" name="lat" value={form.lat} onChange={update} min="-90" step="any" suffix="°" /><Field label="Longitude" name="lon" value={form.lon} onChange={update} min="-180" step="any" suffix="°" /></div><p className="field-hint">For auto-detection, place the coordinates directly on the roof you want to measure.</p><div className="form-section-title">SITE CAPACITY <span>Roof and available recharge area</span></div><div className="fields two"><Field label="Roof area (auto-detect if blank)" name="rooftop_area_m2" value={form.rooftop_area_m2} onChange={update} min="1" required={false} suffix="m²" /><Field label="Open ground area" name="open_area_m2" value={form.open_area_m2} onChange={update} min="0" suffix="m²" /></div><label className="field"><span>Roof material</span><select name="roof_type" value={form.roof_type} onChange={update}><option value="concrete">Concrete</option><option value="tiled">Clay tile</option><option value="gi">Metal / GI sheet</option><option value="asbestos">Fibre cement</option></select></label><div className="form-section-title">WATER NEEDS <span>Plan your storage period</span></div><div className="fields three"><Field label="Household" name="num_persons" value={form.num_persons} onChange={update} min="1" step="1" suffix="people" /><Field label="Daily use / person" name="per_capita" value={form.per_capita} onChange={update} min="1" suffix="L/day" /><Field label="Storage period" name="period_days" value={form.period_days} onChange={update} min="1" step="1" suffix="days" /></div>{error && <div className="error-message" role="alert">{error}</div>}<button className="button button-primary submit-button" type="submit" disabled={loading}>{loading ? <><LoaderCircle className="spin" size={18} /> Analysing your site…</> : <>Generate my plan <ArrowRight size={17} /></>}</button><div className="privacy-note"><Check size={14} /> Your inputs are used only to generate this estimate.</div></motion.form>

    <div className="result-column">{result ? <motion.div className="result-card panel" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}><div className="result-top"><div className="result-kicker"><span className="live-dot" /> YOUR SITE PLAN</div><div className="result-structure">{labels[result.predicted_structure] || formatKey(result.predicted_structure)}</div><p className="result-explanation">{result.explanation}</p></div><div className="metric-cards">{summary.map(({ icon, label, value, tint }) => <div className="metric-card" key={label}><div className={`metric-icon ${tint}`}>{createElement(icon, { size: 17 })}</div><span>{label}</span><b>{value}</b></div>)}</div>{result.rooftop_detection && <div className="detected-roof"><img src={result.rooftop_detection.detection_image} alt="OpenCV highlight of the detected roof" /><div><span>AUTO-DETECTED ROOF</span><b>{Number(result.rooftop_detection.detected_area_m2).toLocaleString("en-IN", { maximumFractionDigits: 1 })} m&#178;</b><small>{result.rooftop_detection.source}</small>{result.rooftop_detection.attribution?.includes("OpenStreetMap") ? <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer">&#169; OpenStreetMap contributors</a> : <small>{result.rooftop_detection.attribution}</small>}</div></div>}<div className="result-section"><div className="result-section-head"><h4>Recommended dimensions</h4><span>ENGINEERING ESTIMATE</span></div><div className="dimension-list">{dimensions.map(([key, value]) => <div key={key}><span>{formatKey(key)}</span><b>{typeof value === 'number' ? `${Number(value).toLocaleString('en-IN', { maximumFractionDigits: 2 })} ${key.endsWith('_l') ? 'L' : key.endsWith('_lps') ? 'L/s' : 'm'}` : value}</b></div>)}</div></div><div className="cost-card"><div className="cost-icon"><Sparkles size={17} /></div><div><span>Indicative project cost</span><b>{money(result.cost_estimate?.total_cost_inr)}</b></div><span className="cost-location">BENGALURU ESTIMATE</span></div>{result.model_diagnostics && <div className="model-note"><span className="live-dot" /> Recommendation cross-checked with the trained model <b>{Math.round((result.model_diagnostics.classifier_confidence || 0) * 100)}% signal</b></div>}<div className="result-foot"><MapPin size={14} /> Based on a nearby observation point {result.nearest_well_record?._distance_km != null && <span>· {Number(result.nearest_well_record._distance_km).toFixed(1)} km away</span>}</div></motion.div> : <div className="empty-result panel"><div className="empty-visual"><div className="empty-ring ring-a" /><div className="empty-ring ring-b" /><div className="empty-drop"><Droplets size={29} /></div></div><div className="empty-copy"><span className="empty-kicker">YOUR PLAN, AT A GLANCE</span><h3>Insights that start<br />with <span>your place.</span></h3><p>Your personalised recommendation will show here, with water potential, suggested structure, dimensions, and an indicative cost.</p></div><div className="empty-footer"><span><i /> Local data</span><span><i /> Practical sizing</span><span><i /> Clear estimates</span></div></div>}</div></div></section>

    <section className="method section-wrap" id="about"><div className="method-intro"><div className="eyebrow"><span className="eyebrow-dot" /> BUILT ON THE RIGHT SIGNALS</div><h2>Useful guidance.<br /><span>Clear reasoning.</span></h2></div><div className="method-points"><div><span>01</span><div><b>Local context matters</b><p>Rainfall, soil, lithology, and water depth inform each site recommendation.</p></div></div><div><span>02</span><div><b>Inputs shape the answer</b><p>Roof material, harvestable area, household demand, and available ground all affect the outcome.</p></div></div><div><span>03</span><div><b>Models with guardrails</b><p>Machine learning informs the recommendation; physical water balance and practical sizing checks keep it grounded.</p></div></div></div></section></main>

    <footer className="footer section-wrap"><a href="#top" className="brand"><span className="brand-mark"><Droplets size={18} /></span><span>ZENKAI<span className="brand-dot">.</span></span></a><span>Rainwater planning, made more considered.</span><a href="#predictor">Build your plan <ArrowRight size={14} /></a></footer>
  </div>
}

export default App
