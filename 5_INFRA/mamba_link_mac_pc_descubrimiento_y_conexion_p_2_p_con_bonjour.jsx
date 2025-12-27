import React, { useMemo, useState } from "react";

const mac_Package_swift = `// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "MambaLinkMac",
    platforms: [ .macOS(.v13) ],
    products: [ .executable(name: "MambaLinkMac", targets: ["MambaLinkMac"]) ],
    targets: [
        .executableTarget(
            name: "MambaLinkMac",
            path: "Sources/MambaLinkMac"
        )
    ]
)`;

const mac_main_swift = `import Foundation
import Network

struct Peer: Hashable {
    let name: String
    let endpoint: NWEndpoint
}

final class MambaLink: NSObject {
    private let serviceType = "_mamba._tcp"
    private let domain = "local."
    private var listener: NWListener?
    private var browser: NWBrowser?
    private var connections: [NWConnection] = []
    private var myUUID: String
    private var advertisedName: String

    private var queue = DispatchQueue(label: "mamba.queue")

    init(name: String? = nil) {
        if let saved = UserDefaults.standard.string(forKey: "mamba.uuid") {
            self.myUUID = saved
        } else {
            self.myUUID = UUID().uuidString
            UserDefaults.standard.set(self.myUUID, forKey: "mamba.uuid")
        }
        self.advertisedName = name ?? Host.current().localizedName ?? "Mac"
        super.init()
    }

    func start() {
        startListening()
        startBrowsing()
        print("[mac] UUID=\(myUUID) anunciando y navegando...")
        dispatchMain()
    }

    private func startListening() {
        do {
            listener = try NWListener(using: .tcp)
        } catch {
            fatalError("No se pudo crear listener: \(error)")
        }

        listener?.service = NWListener.Service(name: advertisedName, type: serviceType, domain: domain)

        listener?.newConnectionHandler = { [weak self] conn in
            guard let self = self else { return }
            self.setupConnection(conn, isOutbound: false)
        }

        listener?.stateUpdateHandler = { state in
            switch state {
            case .ready:
                if let port = self.listener?.port { print("[mac] Listener listo en puerto \(port)") }
            case .failed(let err):
                print("[mac] Listener falló: \(err)")
            default: break
            }
        }
        listener?.start(queue: queue)
    }

    private func startBrowsing() {
        browser = NWBrowser(for: .bonjour(type: serviceType, domain: domain), using: NWParameters.tcp)
        browser?.browseResultsChangedHandler = { [weak self] results, _ in
            guard let self = self else { return }
            for result in results {
                switch result.endpoint {
                case .service(let name, _, _, _):
                    if name == self.advertisedName { continue }
                    self.resolveAndMaybeConnect(result: result)
                default: break
                }
            }
        }
        browser?.stateUpdateHandler = { state in
            switch state {
            case .ready: print("[mac] Navegando Bonjour listo")
            case .failed(let err): print("[mac] Browser falló: \(err)")
            default: break
            }
        }
        browser?.start(queue: queue)
    }

    private func resolveAndMaybeConnect(result: NWBrowser.Result) {
        let endpoint = result.endpoint
        let conn = NWConnection(to: endpoint, using: .tcp)
        connections.append(conn)
        conn.stateUpdateHandler = { [weak self] state in
            guard let self = self else { return }
            switch state {
            case .ready:
                self.performHandshake(on: conn, isOutbound: true)
            case .failed(let err):
                print("[mac] Resolución/conn falló: \(err)")
                self.removeConnection(conn)
            case .cancelled:
                self.removeConnection(conn)
            default: break
            }
        }
        conn.start(queue: queue)
    }

    private func setupConnection(_ conn: NWConnection, isOutbound: Bool) {
        connections.append(conn)
        conn.stateUpdateHandler = { [weak self] state in
            guard let self = self else { return }
            switch state {
            case .ready:
                print("[mac] Conexión lista (\(isOutbound ? "saliente" : "entrante"))")
                self.receive(on: conn)
                if !isOutbound { self.performHandshake(on: conn, isOutbound: false) }
            case .failed(let err):
                print("[mac] Conexión falló: \(err)")
                self.removeConnection(conn)
            case .cancelled:
                self.removeConnection(conn)
            default: break
            }
        }
        conn.start(queue: queue)
    }

    private func removeConnection(_ conn: NWConnection) {
        if let i = connections.firstIndex(where: { $0 === conn }) { connections.remove(at: i) }
    }

    private func performHandshake(on conn: NWConnection, isOutbound: Bool) {
        let hello: [String: Any] = [
            "type": "hello",
            "id": myUUID,
            "token": "MAMBA1"
        ]
        if let data = try? JSONSerialization.data(withJSONObject: hello) {
            var payload = data
            payload.append(0x0A)
            conn.send(content: payload, completion: .contentProcessed({ _ in
                self.receive(on: conn)
            }))
        }
    }

    private func receive(on conn: NWConnection) {
        conn.receive(minimumIncompleteLength: 1, maximumLength: 4096) { [weak self] data, _, isComplete, err in
            guard let self = self else { return }
            if let data = data, !data.isEmpty {
                if let line = String(data: data, encoding: .utf8) {
                    for raw in line.split(separator: "\n") {
                        self.handleLine(String(raw), from: conn)
                    }
                }
            }
            if isComplete || err != nil { conn.cancel(); return }
            self.receive(on: conn)
        }
    }

    private func handleLine(_ line: String, from conn: NWConnection) {
        guard let json = try? JSONSerialization.jsonObject(with: Data(line.utf8)) as? [String: Any] else {
            print("[mac] línea no-json: \(line)")
            return
        }
        if json["type"] as? String == "hello", let peerId = json["id"] as? String {
            print("[mac] HELLO de peer id=\(peerId)")
        }
    }
}

let app = MambaLink()
app.start()`;

const win_main_py = `import socket
import threading
import json
import time
from zeroconf import ServiceInfo, Zeroconf, ServiceBrowser

SERVICE_TYPE = "_mamba._tcp.local."
TOKEN = "MAMBA1"

class TCPServer(threading.Thread):
    def __init__(self, host="0.0.0.0", port=0, on_client=None):
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        self.on_client = on_client
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)
        self.port = self.sock.getsockname()[1]
        self._stop = threading.Event()

    def run(self):
        while not self._stop.is_set():
            try:
                self.sock.settimeout(1)
                conn, addr = self.sock.accept()
            except socket.timeout:
                continue
            threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()

    def handle_client(self, conn, addr):
        if self.on_client:
            self.on_client(conn, addr)

    def stop(self):
        self._stop.set()
        try:
            self.sock.close()
        except:
            pass

class PeerBrowser:
    def __init__(self, zeroconf, on_service):
        self.zeroconf = zeroconf
        self.on_service = on_service
        self.browser = ServiceBrowser(zeroconf, SERVICE_TYPE, handlers=[self._on_state_change])

    def _on_state_change(self, zeroconf, service_type, name, state_change):
        if state_change.name == "Added":
            info = zeroconf.get_service_info(service_type, name)
            if info:
                self.on_service(info)

class MambaWin:
    def __init__(self):
        self.uuid = self._get_or_make_uuid()
        self.name = socket.gethostname()
        self.zeroconf = Zeroconf()
        self.server = TCPServer(on_client=self.on_client)
        self.server.start()
        self.register_service()
        self.browser = PeerBrowser(self.zeroconf, self.on_service_found)
        print(f"[win] UUID={self.uuid} anunciando en puerto {self.server.port}")

    def _get_or_make_uuid(self):
        import pathlib, uuid
        p = pathlib.Path.home() / ".mamba_uuid"
        if p.exists():
            return p.read_text().strip()
        u = str(uuid.uuid4())
        p.write_text(u)
        return u

    def register_service(self):
        info = ServiceInfo(
            type_=SERVICE_TYPE,
            name=f"{self.name}.{SERVICE_TYPE}",
            addresses=[socket.inet_aton(self._get_ip())],
            port=self.server.port,
            properties={b"id": self.uuid.encode("utf-8")},
        )
        self.zeroconf.register_service(info)

    def _get_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
        return ip

    def on_service_found(self, info: ServiceInfo):
        if info.properties.get(b"id", b"").decode("utf-8") == self.uuid:
            return
        host = socket.inet_ntoa(info.addresses[0]) if info.addresses else None
        port = info.port
        if not host:
            return
        peer_id = info.properties.get(b"id", b"").decode("utf-8")
        should_initiate = True if not peer_id else (self.uuid < peer_id)
        if should_initiate:
            threading.Thread(target=self.connect_and_handshake, args=(host, port), daemon=True).start()

    def connect_and_handshake(self, host, port):
        try:
            with socket.create_connection((host, port), timeout=5) as s:
                hello = json.dumps({"type":"hello","id": self.uuid, "token": TOKEN}) + "\n"
                s.sendall(hello.encode("utf-8"))
                try:
                    s.settimeout(3)
                    data = s.recv(4096)
                    if data:
                        for line in data.splitlines():
                            self.handle_line(line.decode("utf-8"))
                except socket.timeout:
                    pass
        except Exception as e:
            print(f"[win] Error conectando a {host}:{port} -> {e}")

    def on_client(self, conn, addr):
        try:
            data = conn.recv(4096)
            if data:
                for line in data.splitlines():
                    self.handle_line(line.decode("utf-8"))
            hello = json.dumps({"type":"hello","id": self.uuid, "token": TOKEN}) + "\n"
            conn.sendall(hello.encode("utf-8"))
        except Exception as e:
            print(f"[win] Error cliente {addr}: {e}")
        finally:
            try: conn.close()
            except: pass

    def handle_line(self, line: str):
        try:
            obj = json.loads(line)
        except:
            print(f"[win] linea no-json: {line}")
            return
        if obj.get("type") == "hello":
            print(f"[win] HELLO de {obj.get('id')}")

    def run(self):
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.zeroconf.close()
            self.server.stop()

if __name__ == "__main__":
    MambaWin().run()`;

const readmeText = `MambaLink — Mac & PC (Bonjour/mDNS)

Protocolo
- Ambos anuncian _mamba._tcp(.local)
- Regla: UUID lexicográficamente menor inicia
- Handshake JSON line-based: {"type":"hello","id":"<uuid>","token":"MAMBA1"}+"\n"

macOS
1) mkdir MambaLinkMac && cd MambaLinkMac
2) swift package init --type executable
3) Crea: Sources/MambaLinkMac/main.swift  (pega mac_main_swift)
4) Reemplaza Package.swift (pega mac_Package_swift)
5) swift run

Windows
1) py -m pip install zeroconf
2) python main.py (pega win_main_py en mamba_win/main.py)

Firewalls
- Permitir mDNS UDP 5353 y TCP saliente/entrante local
`;

function buildHello(uuid) {
  return JSON.stringify({ type: "hello", id: uuid, token: "MAMBA1" }) + "\n";
}
function shouldInitiate(uuidSelf, uuidPeer) {
  if (!uuidPeer) return true;
  return uuidSelf < uuidPeer;
}
function serviceTypeMac() { return "_mamba._tcp"; }
function serviceTypeWin() { return "_mamba._tcp.local."; }

function runTests() {
  const tests = [];
  function t(name, fn) {
    try { const v = fn(); tests.push({ name, ok: true, details: v }); }
    catch (e) { tests.push({ name, ok: false, details: String(e) }); }
  }
  function assert(cond, msg = "Assertion failed") {
    if (!cond) throw new Error(msg);
  }
  function assertEq(a, b) {
    if (a !== b) throw new Error(`Expected ${String(b)} but got ${String(a)}`);
  }
  t("Handshake string includes newline", () => {
    const s = buildHello("abc");
    assert(s.endsWith("\n"));
    return s.length;
  });
  t("Handshake JSON has correct token", () => {
    const s = buildHello("abc").trim();
    const obj = JSON.parse(s);
    assertEq(obj.token, "MAMBA1");
    return obj.token;
  });
  t("UUID lexicographic rule: self < peer → initiate", () => {
    assert(shouldInitiate("00000000", "ffffffff"));
    return true;
  });
  t("UUID lexicographic rule: self > peer → do not initiate", () => {
    assert(!shouldInitiate("ffffffff", "00000000"));
    return true;
  });
  t("Unknown peer id → initiate", () => {
    assert(shouldInitiate("abc", ""));
    return true;
  });
  t("mac service type", () => { assertEq(serviceTypeMac(), "_mamba._tcp"); return serviceTypeMac(); });
  t("win service type", () => { assertEq(serviceTypeWin(), "_mamba._tcp.local."); return serviceTypeWin(); });
  t("Line split compatibility", () => {
    const packet = [buildHello("u1"), buildHello("u2")].join("");
    const lines = packet.split("\n").filter(Boolean);
    assertEq(lines.length, 2);
    const objs = lines.map((l) => JSON.parse(l));
    assert(objs.every((o) => o.type === "hello"));
    return lines.length;
  });
  return tests;
}

function CodeBlock({ title, filename, code }) {
  const [copied, setCopied] = useState(false);
  const onCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 1200);
    } catch (_) {}
  };
  return (
    <div className="rounded-2xl shadow p-4 border mb-6">
      <div className="flex items-center justify-between mb-2">
        <div>
          <div className="text-sm opacity-70">{title}</div>
          <div className="font-mono text-xs opacity-60">{filename}</div>
        </div>
        <button onClick={onCopy} className="px-3 py-1 rounded-xl border hover:shadow">
          {copied ? "Copied" : "Copy"}
        </button>
      </div>
      <pre className="overflow-auto text-sm leading-relaxed" style={{whiteSpace: "pre-wrap"}}>
        <code>{code}</code>
      </pre>
    </div>
  );
}

function TestsPanel() {
  const [results, setResults] = useState([]);
  const [ran, setRan] = useState(false);
  const doRun = () => {
    const r = runTests();
    setResults(r);
    setRan(true);
  };
  const allOk = useMemo(() => results.length > 0 && results.every(r => r.ok), [results]);
  return (
    <div className="rounded-2xl shadow p-4 border">
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-semibold">Self‑tests</h3>
        <button onClick={doRun} className="px-3 py-1 rounded-xl border hover:shadow">Run tests</button>
      </div>
      {!ran && <p className="opacity-70 text-sm">Click “Run tests” to validate protocol assumptions.</p>}
      {ran && (
        <div>
          <div className={`mb-3 text-sm ${allOk ? 'text-green-700' : 'text-red-700'}`}>
            {allOk ? 'All tests passed' : 'Some tests failed — see details below'}
          </div>
          <ul className="space-y-1">
            {results.map((r, i) => (
              <li key={i} className={`text-sm ${r.ok ? 'text-green-700' : 'text-red-700'}`}>
                {r.ok ? '✓' : '✗'} {r.name}
                {r.details !== undefined && (
                  <span className="opacity-60"> — {String(r.details)}</span>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function Troubleshooting() {
  return (
    <div className="rounded-2xl shadow p-4 border">
      <h3 className="font-semibold mb-2">Troubleshooting</h3>
      <ul className="list-disc pl-5 text-sm space-y-1">
        <li>Both devices must be on the same LAN or mDNS‑routed network. Allow UDP 5353 and local TCP in firewalls.</li>
        <li>Windows: <code>pip install zeroconf</code>; macOS: Xcode / Swift toolchain installed.</li>
        <li>If you want mutual TLS later: use <code>NWParameters.tls</code> on macOS and <code>ssl</code> in Python.</li>
        <li>If two peers share the same hostname, we still disambiguate with UUID at handshake level.</li>
      </ul>
    </div>
  );
}

export default function MambaLinkDocs() {
  const [tab, setTab] = useState("readme");
  return (
    <div className="p-6 space-y-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-bold">MambaLink (Mac & PC) — Descubrimiento y Conexión P2P con Bonjour</h1>
        <p className="opacity-70 text-sm">Swift (macOS) + Python (Windows) • Bonjour/mDNS • JSON line‑based handshake</p>
      </header>
      <nav className="flex gap-2">
        {[
          ["readme", "README"],
          ["mac_pkg", "macOS • Package.swift"],
          ["mac_main", "macOS • main.swift"],
          ["win_main", "Windows • main.py"],
          ["tests", "Self‑tests"],
          ["help", "Troubleshooting"],
        ].map(([key, label]) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={`px-3 py-1 rounded-xl border hover:shadow ${tab===key? 'bg-black text-white' : ''}`}
          >{label}</button>
        ))}
      </nav>
      {tab === "readme" && (
        <div className="rounded-2xl shadow p-4 border">
          <pre className="text-sm" style={{whiteSpace: 'pre-wrap'}}>{readmeText}</pre>
        </div>
      )}
      {tab === "mac_pkg" && (
        <CodeBlock title="macOS — Package.swift" filename="Package.swift" code={mac_Package_swift} />
      )}
      {tab === "mac_main" && (
        <CodeBlock title="macOS — Sources/MambaLinkMac/main.swift" filename="main.swift" code={mac_main_swift} />
      )}
      {tab === "win_main" && (
        <CodeBlock title="Windows — mamba_win/main.py" filename="main.py" code={win_main_py} />
      )}
      {tab === "tests" && <TestsPanel />}
      {tab === "help" && <Troubleshooting />}
      <footer className="opacity-60 text-xs">
        © {new Date().getFullYear()} BlackMamba • Protocol token: MAMBA1 • Service types: mac <code>_mamba._tcp</code> | win <code>_mamba._tcp.local.</code>
      </footer>
    </div>
  );
}
