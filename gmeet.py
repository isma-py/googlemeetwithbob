import streamlit as st
import streamlit.components.v1 as components

# Konfigurasi skrin penuh & responsive
st.set_page_config(
    page_title="Google Meet Clone",
    page_icon="📹",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hilangkan margin/padding Streamlit
st.markdown("""
    <style>
        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            padding-left: 0rem !important;
            padding-right: 0rem !important;
            max-width: 100% !important;
        }
        header {visibility: hidden !important;}
        footer {visibility: hidden !important;}
        [data-testid="stHeader"] {display: none;}
        iframe {
            width: 100% !important;
            height: 100dvh !important;
            border: none !important;
        }
    </style>
""", unsafe_allow_html=True)

meet_html_code = """
<!DOCTYPE html>
<html lang="ms">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Google Meet Clone</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
    <!-- Library QR Code Generator -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        * { box-sizing: border-box; touch-action: manipulation; }
        body { 
            background-color: #202124; 
            color: white; 
            font-family: 'Google Sans', Roboto, Arial, sans-serif; 
            height: 100dvh; 
            width: 100vw;
            overflow: hidden; 
            margin: 0;
            padding: 0;
        }
        .video-grid { 
            display: grid; 
            gap: 0.75rem; 
            align-content: center; 
            justify-content: center; 
            width: 100%;
            height: 100%;
            padding: 0.75rem; 
            overflow-y: auto;
        }
        .video-card { 
            position: relative; 
            background-color: #3c4043; 
            border-radius: 0.75rem; 
            overflow: hidden; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            width: 100%; 
            height: 100%; 
            min-height: 180px;
            transition: all 0.3s ease; 
        }
        video { width: 100%; height: 100%; object-fit: cover; transform: scaleX(-1); }
        .avatar { width: 72px; height: 72px; border-radius: 50%; background-color: #1a73e8; display: flex; align-items: center; justify-content: center; font-size: 2rem; font-weight: bold; }
        .blur-video { filter: blur(8px); }

        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-thumb { background: #5f6368; border-radius: 4px; }
    </style>
</head>
<body class="flex flex-col justify-between">

    <!-- Pre-join Screen / Lobby -->
    <div id="lobby" class="fixed inset-0 z-50 bg-[#202124] flex items-center justify-center p-4 overflow-y-auto">
        <div class="max-w-4xl w-full grid grid-cols-1 md:grid-cols-2 gap-6 items-center my-auto">
            <div class="flex flex-col items-center w-full">
                <div class="relative w-full aspect-video bg-[#3c4043] rounded-2xl overflow-hidden flex items-center justify-center border border-gray-700 shadow-2xl">
                    <video id="preview-video" autoplay playsinline muted class="w-full h-full object-cover"></video>
                    <div id="preview-avatar" class="avatar hidden">Anda</div>
                    <div class="absolute bottom-3 flex gap-3">
                        <button onclick="togglePreviewMic()" id="btn-prev-mic" class="p-3 rounded-full bg-gray-700/80 backdrop-blur hover:bg-gray-600 text-white transition">
                            <i class="fas fa-microphone" id="icon-prev-mic"></i>
                        </button>
                        <button onclick="togglePreviewCam()" id="btn-prev-cam" class="p-3 rounded-full bg-gray-700/80 backdrop-blur hover:bg-gray-600 text-white transition">
                            <i class="fas fa-video" id="icon-prev-cam"></i>
                        </button>
                    </div>
                </div>
            </div>

            <div class="space-y-4 w-full">
                <div>
                    <h1 class="text-2xl md:text-3xl font-normal text-white">Sertai Mesyuarat</h1>
                    <p class="text-gray-400 text-xs md:text-sm mt-1">Sertai melalui Imbasan QR Code atau ID Bilik</p>
                </div>
                <div class="space-y-3">
                    <input type="text" id="username" placeholder="Nama Anda" class="w-full px-4 py-3 bg-[#202124] border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 text-white text-sm" />
                    <div class="flex flex-col sm:flex-row gap-2">
                        <input type="text" id="room-id-input" placeholder="Kod / ID Bilik (Contoh: bilik123)" class="flex-1 px-4 py-3 bg-[#202124] border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 text-white text-sm" />
                        <button onclick="joinRoom()" class="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition text-sm">Sertai</button>
                    </div>
                    <div class="relative flex py-1 items-center">
                        <div class="flex-grow border-t border-gray-700"></div>
                        <span class="flex-shrink mx-3 text-gray-500 text-xs uppercase">atau</span>
                        <div class="flex-grow border-t border-gray-700"></div>
                    </div>
                    <button onclick="createRoom()" class="w-full py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-medium rounded-lg transition text-sm">
                        <i class="fas fa-plus mr-2"></i>Cipta Bilik Baru
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- Main Meeting UI -->
    <div id="main-ui" class="hidden flex-1 flex flex-col relative h-[100dvh] w-full overflow-hidden">
        <!-- Top Header Navigation -->
        <div class="h-12 md:h-14 bg-[#171717] px-3 md:px-6 flex items-center justify-between border-b border-gray-800 flex-shrink-0">
            <div class="flex items-center gap-2 md:gap-3">
                <button onclick="backToLobby()" class="flex items-center gap-1.5 px-2.5 py-1.5 bg-gray-800 hover:bg-gray-700 text-gray-200 rounded-lg text-xs md:text-sm transition">
                    <i class="fas fa-arrow-left"></i>
                    <span class="hidden sm:inline">Kembali</span>
                </button>
                <span class="text-xs md:text-sm font-medium text-gray-300 truncate max-w-[140px] sm:max-w-none" id="header-room-title">Google Meet</span>
            </div>
            <div class="flex items-center gap-2">
                <button onclick="showQRCodeModal()" class="flex items-center gap-1.5 px-3 py-1 bg-blue-600/30 border border-blue-500/50 hover:bg-blue-600/50 text-blue-300 rounded-full text-xs transition">
                    <i class="fas fa-qrcode"></i>
                    <span>Kod QR</span>
                </button>
                <div class="flex items-center gap-1.5 text-[10px] md:text-xs text-emerald-400 bg-emerald-950/40 border border-emerald-800/50 px-2.5 py-1 rounded-full">
                    <i class="fas fa-signal"></i>
                    <span id="status-tag">Connected</span>
                </div>
            </div>
        </div>

        <div class="flex-1 flex relative overflow-hidden w-full">
            <!-- Dynamic Video Grid -->
            <div id="video-grid" class="video-grid w-full">
                <!-- Local User Card -->
                <div class="video-card" id="local-card">
                    <video id="local-video" autoplay playsinline muted></video>
                    <div id="local-avatar" class="avatar hidden">A</div>
                    <div class="absolute bottom-2 left-2 bg-black/60 backdrop-blur px-2.5 py-1 rounded-md text-[11px] flex items-center gap-1.5">
                        <span id="local-name-tag">Anda</span>
                        <span id="local-hand-status" class="hidden text-amber-400"><i class="fas fa-hand"></i></span>
                    </div>
                </div>
            </div>

            <!-- Sidebar Chat -->
            <div id="sidebar-chat" class="hidden absolute md:relative right-0 top-0 z-40 w-full sm:w-80 bg-[#171717] border-l border-gray-800 flex flex-col h-full shadow-2xl">
                <div class="p-3 md:p-4 border-b border-gray-800 flex justify-between items-center">
                    <h2 class="font-medium text-xs md:text-sm">Mesej Panggilan</h2>
                    <button onclick="toggleSidebar('chat')" class="text-gray-400 hover:text-white p-1"><i class="fas fa-times"></i></button>
                </div>
                <div id="chat-messages" class="flex-1 p-3 md:p-4 overflow-y-auto space-y-2.5 text-xs md:text-sm"></div>
                <div class="p-3 md:p-4 border-t border-gray-800 flex gap-2">
                    <input type="text" id="chat-input" placeholder="Hantar mesej..." class="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-xs md:text-sm focus:outline-none focus:border-blue-500" onkeypress="if(event.key==='Enter') sendChatMessage()">
                    <button onclick="sendChatMessage()" class="p-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white"><i class="fas fa-paper-plane"></i></button>
                </div>
            </div>
        </div>

        <!-- Bottom Control Toolbar -->
        <div class="h-16 md:h-20 bg-[#202124] border-t border-gray-800 px-2 md:px-6 flex items-center justify-between flex-shrink-0">
            <div class="hidden md:flex items-center gap-2 text-gray-300">
                <span id="display-room-id" class="font-mono text-xs bg-gray-800 px-3 py-1.5 rounded-lg border border-gray-700"></span>
                <button onclick="copyRoomLink()" class="p-2 hover:bg-gray-800 rounded-lg text-gray-400 hover:text-white transition" title="Salin ID Bilik">
                    <i class="far fa-copy"></i>
                </button>
            </div>

            <!-- Buttons -->
            <div class="flex items-center justify-center gap-2 sm:gap-3 w-full md:w-auto">
                <button onclick="toggleMic()" id="btn-mic" class="p-3 sm:p-3.5 rounded-full bg-gray-700 hover:bg-gray-600 text-white transition">
                    <i class="fas fa-microphone" id="icon-mic"></i>
                </button>
                <button onclick="toggleCam()" id="btn-cam" class="p-3 sm:p-3.5 rounded-full bg-gray-700 hover:bg-gray-600 text-white transition">
                    <i class="fas fa-video" id="icon-cam"></i>
                </button>
                <button onclick="showQRCodeModal()" class="p-3 sm:p-3.5 rounded-full bg-gray-700 hover:bg-gray-600 text-white transition" title="Papar Kod QR">
                    <i class="fas fa-qrcode"></i>
                </button>
                <button onclick="toggleBlur()" id="btn-blur" class="p-3 sm:p-3.5 rounded-full bg-gray-700 hover:bg-gray-600 text-white transition">
                    <i class="fas fa-wand-magic-sparkles"></i>
                </button>
                <button onclick="toggleRaiseHand()" id="btn-hand" class="p-3 sm:p-3.5 rounded-full bg-gray-700 hover:bg-gray-600 text-white transition">
                    <i class="fas fa-hand"></i>
                </button>
                <button onclick="toggleScreenShare()" id="btn-screen" class="hidden sm:block p-3.5 rounded-full bg-gray-700 hover:bg-gray-600 text-white transition">
                    <i class="fas fa-desktop"></i>
                </button>
                <button onclick="toggleSidebar('chat')" class="md:hidden p-3 rounded-full bg-gray-700 hover:bg-gray-600 text-white transition">
                    <i class="far fa-comment-alt"></i>
                </button>
                <button onclick="backToLobby()" class="p-3 sm:p-3.5 rounded-full bg-red-600 hover:bg-red-700 text-white px-4 sm:px-6 transition flex items-center gap-1.5">
                    <i class="fas fa-phone-slash"></i>
                    <span class="text-xs font-semibold hidden sm:inline">Keluar</span>
                </button>
            </div>

            <div class="hidden md:flex items-center gap-2">
                <button onclick="toggleSidebar('chat')" class="p-3 rounded-full hover:bg-gray-800 text-gray-300 transition">
                    <i class="far fa-comment-alt"></i>
                </button>
            </div>
        </div>
    </div>

    <!-- QR Code Modal Pop-up -->
    <div id="qr-modal" class="hidden fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
        <div class="bg-[#28292c] border border-gray-700 rounded-2xl p-6 max-w-sm w-full flex flex-col items-center text-center shadow-2xl relative">
            <button onclick="closeQRCodeModal()" class="absolute top-4 right-4 text-gray-400 hover:text-white text-lg">
                <i class="fas fa-times"></i>
            </button>
            <h3 class="text-lg font-medium text-white mb-1">Imbas Untuk Sertai</h3>
            <p class="text-xs text-gray-400 mb-4">Minta rakan anda imbas Kod QR ini menggunakan kamera peranti mereka.</p>
            
            <div id="qrcode-container" class="bg-white p-3 rounded-xl shadow-lg mb-4"></div>
            
            <div class="w-full bg-[#1e1f21] border border-gray-700 rounded-lg p-2.5 flex items-center justify-between text-xs mb-3">
                <span id="qr-link-text" class="text-gray-300 truncate max-w-[200px] font-mono"></span>
                <button onclick="copyRoomLink()" class="text-blue-400 hover:text-blue-300 ml-2 flex-shrink-0">
                    <i class="far fa-copy mr-1"></i>Salin
                </button>
            </div>
        </div>
    </div>

    <script>
        let localStream;
        let peer;
        let myPeerId;
        let currentRoomId;
        let myName = "Pengguna";
        let isMicOn = true;
        let isCamOn = true;
        let isBlurred = false;
        let isHandRaised = false;
        
        let activeCalls = {};
        let dataConns = {};
        let connectedPeersSet = new Set();
        let qrCodeObj = null;

        const iceServers = {
            iceServers: [
                { urls: 'stun:stun.l.google.com:19302' },
                { urls: 'stun:stun1.l.google.com:19302' },
                { urls: 'stun:stun2.l.google.com:19302' },
                { urls: 'stun:stun3.l.google.com:19302' },
                { urls: 'stun:stun4.l.google.com:19302' }
            ]
        };

        // Semak jika ada parameter ?room=xxx dari URL (Imbasan Kod QR)
        function checkURLParams() {
            const urlParams = new URLSearchParams(window.location.search);
            const roomParam = urlParams.get('room');
            if (roomParam) {
                document.getElementById('room-id-input').value = roomParam;
            }
        }

        async function initPreview() {
            checkURLParams();
            try {
                localStream = await navigator.mediaDevices.getUserMedia({
                    video: { width: { max: 1280 }, height: { max: 720 }, facingMode: "user" },
                    audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true }
                });
                document.getElementById('preview-video').srcObject = localStream;
            } catch (err) {
                console.error("Camera/Mic access error:", err);
            }
        }
        initPreview();

        function togglePreviewMic() {
            isMicOn = !isMicOn;
            if(localStream) localStream.getAudioTracks().forEach(t => t.enabled = isMicOn);
            document.getElementById('icon-prev-mic').className = isMicOn ? 'fas fa-microphone' : 'fas fa-microphone-slash text-red-500';
            document.getElementById('icon-mic').className = isMicOn ? 'fas fa-microphone' : 'fas fa-microphone-slash text-red-500';
        }

        function togglePreviewCam() {
            isCamOn = !isCamOn;
            if(localStream) localStream.getVideoTracks().forEach(t => t.enabled = isCamOn);
            document.getElementById('icon-prev-cam').className = isCamOn ? 'fas fa-video' : 'fas fa-video-slash text-red-500';
            document.getElementById('icon-cam').className = isCamOn ? 'fas fa-video' : 'fas fa-video-slash text-red-500';
            document.getElementById('preview-video').classList.toggle('hidden', !isCamOn);
            document.getElementById('preview-avatar').classList.toggle('hidden', isCamOn);
            document.getElementById('local-video').classList.toggle('hidden', !isCamOn);
            document.getElementById('local-avatar').classList.toggle('hidden', isCamOn);
        }

        function createRoom() {
            const randomId = 'room-' + Math.random().toString(36).substring(2, 8);
            document.getElementById('room-id-input').value = randomId;
            joinRoom();
        }

        function joinRoom() {
            const nameInput = document.getElementById('username').value.trim();
            const roomInput = document.getElementById('room-id-input').value.trim().toLowerCase();
            
            if(!roomInput) { alert("Sila masukkan ID Bilik."); return; }
            if(nameInput) myName = nameInput;

            currentRoomId = roomInput;
            const hostPeerId = "host-" + currentRoomId;

            document.getElementById('local-name-tag').innerText = myName + " (Anda)";
            document.getElementById('local-avatar').innerText = myName.charAt(0).toUpperCase();
            document.getElementById('display-room-id').innerText = "ID: " + currentRoomId;
            document.getElementById('header-room-title').innerText = "Bilik: " + currentRoomId;

            document.getElementById('lobby').classList.add('hidden');
            document.getElementById('main-ui').classList.remove('hidden');
            document.getElementById('local-video').srcObject = localStream;

            peer = new Peer(hostPeerId, { config: iceServers });

            peer.on('open', id => {
                myPeerId = id;
                document.getElementById('status-tag').innerText = "Host (Room Owner)";
                setupPeerListeners();
            });

            peer.on('error', err => {
                if(err.type === 'unavailable-id') {
                    myPeerId = "client-" + Math.random().toString(36).substring(2, 9);
                    peer = new Peer(myPeerId, { config: iceServers });

                    peer.on('open', id => {
                        document.getElementById('status-tag').innerText = "Client Connected";
                        setupPeerListeners();
                        connectToHost(hostPeerId);
                    });
                } else {
                    console.error("PeerJS Error:", err);
                }
            });
        }

        function setupPeerListeners() {
            peer.on('call', call => {
                call.answer(localStream);
                activeCalls[call.peer] = call;

                call.on('stream', remoteStream => {
                    addRemoteStream(call.peer, remoteStream);
                });

                call.on('close', () => {
                    removeRemoteStream(call.peer);
                });
            });

            peer.on('connection', conn => {
                handleDataConnection(conn);
            });
        }

        function connectToHost(hostId) {
            const conn = peer.connect(hostId, { metadata: { name: myName } });
            handleDataConnection(conn);

            const call = peer.call(hostId, localStream);
            if(call) {
                activeCalls[hostId] = call;
                call.on('stream', remoteStream => {
                    addRemoteStream(hostId, remoteStream);
                });
                call.on('close', () => {
                    removeRemoteStream(hostId);
                });
            }
        }

        function handleDataConnection(conn) {
            dataConns[conn.peer] = conn;
            connectedPeersSet.add(conn.peer);

            conn.on('data', data => {
                if(data.type === 'chat') {
                    appendChatMessage(data.sender, data.message);
                } else if(data.type === 'peer-list') {
                    data.peers.forEach(peerId => {
                        if(peerId !== myPeerId && !activeCalls[peerId]) {
                            callOtherPeer(peerId);
                        }
                    });
                }
            });

            conn.on('open', () => {
                if(myPeerId.startsWith('host-')) {
                    const peerList = Array.from(connectedPeersSet);
                    conn.send({ type: 'peer-list', peers: peerList });
                }
            });

            conn.on('close', () => {
                delete dataConns[conn.peer];
                connectedPeersSet.delete(conn.peer);
                removeRemoteStream(conn.peer);
            });
        }

        function callOtherPeer(targetPeerId) {
            const conn = peer.connect(targetPeerId, { metadata: { name: myName } });
            handleDataConnection(conn);

            const call = peer.call(targetPeerId, localStream);
            if(call) {
                activeCalls[targetPeerId] = call;
                call.on('stream', remoteStream => {
                    addRemoteStream(targetPeerId, remoteStream);
                });
                call.on('close', () => {
                    removeRemoteStream(targetPeerId);
                });
            }
        }

        function addRemoteStream(peerId, stream) {
            if(document.getElementById(`card-${peerId}`)) return;

            const grid = document.getElementById('video-grid');
            const card = document.createElement('div');
            card.className = 'video-card';
            card.id = `card-${peerId}`;

            const video = document.createElement('video');
            video.srcObject = stream;
            video.autoplay = true;
            video.playsInline = true;

            const tag = document.createElement('div');
            tag.className = 'absolute bottom-2 left-2 bg-black/60 backdrop-blur px-2.5 py-1 rounded-md text-[11px]';
            tag.innerText = `Peserta (${peerId.substring(0, 8)})`;

            card.appendChild(video);
            card.appendChild(tag);
            grid.appendChild(card);
            adjustGrid();
        }

        function removeRemoteStream(peerId) {
            const card = document.getElementById(`card-${peerId}`);
            if(card) card.remove();
            adjustGrid();
        }

        function adjustGrid() {
            const grid = document.getElementById('video-grid');
            const count = grid.children.length;
            const isMobile = window.innerWidth < 640;

            if(isMobile) {
                if(count === 1) grid.className = "video-grid w-full grid-cols-1";
                else grid.className = "video-grid w-full grid-cols-1 auto-rows-fr";
            } else {
                if(count <= 1) grid.className = "video-grid w-full grid-cols-1";
                else if(count === 2) grid.className = "video-grid w-full grid-cols-1 md:grid-cols-2";
                else grid.className = "video-grid w-full grid-cols-2 md:grid-cols-3";
            }
        }

        window.addEventListener('resize', adjustGrid);

        function toggleMic() { togglePreviewMic(); }
        function toggleCam() { togglePreviewCam(); }

        function toggleBlur() {
            isBlurred = !isBlurred;
            document.getElementById('local-video').classList.toggle('blur-video', isBlurred);
            document.getElementById('btn-blur').classList.toggle('bg-blue-600', isBlurred);
        }

        function toggleRaiseHand() {
            isHandRaised = !isHandRaised;
            document.getElementById('local-hand-status').classList.toggle('hidden', !isHandRaised);
            document.getElementById('btn-hand').classList.toggle('bg-amber-600', isHandRaised);
        }

        async function toggleScreenShare() {
            try {
                const screenStream = await navigator.mediaDevices.getDisplayMedia({ video: true });
                const videoTrack = screenStream.getVideoTracks()[0];
                
                document.getElementById('local-video').srcObject = screenStream;

                videoTrack.onended = () => {
                    document.getElementById('local-video').srcObject = localStream;
                };
            } catch(err) {
                console.error("Screen share canceled:", err);
            }
        }

        function toggleSidebar(type) {
            const chat = document.getElementById('sidebar-chat');
            chat.classList.toggle('hidden');
        }

        function sendChatMessage() {
            const input = document.getElementById('chat-input');
            const msg = input.value.trim();
            if(!msg) return;

            appendChatMessage('Anda', msg);
            Object.values(dataConns).forEach(conn => {
                conn.send({ type: 'chat', sender: myName, message: msg });
            });
            input.value = '';
        }

        function appendChatMessage(sender, msg) {
            const container = document.getElementById('chat-messages');
            const div = document.createElement('div');
            div.className = 'bg-gray-800 p-2.5 rounded-lg border border-gray-700/50';
            div.innerHTML = `<span class="font-semibold text-[11px] text-blue-400 block mb-0.5">${sender}</span><span class="text-gray-200 text-xs">${msg}</span>`;
            container.appendChild(div);
            container.scrollTop = container.scrollHeight;
        }

        // Fungsi Jana Kod QR & Salin Link
        function getDirectRoomURL() {
            const baseUrl = window.location.origin + window.location.pathname;
            return `${baseUrl}?room=${currentRoomId}`;
        }

        function showQRCodeModal() {
            const fullLink = getDirectRoomURL();
            document.getElementById('qr-link-text').innerText = fullLink;

            const container = document.getElementById('qrcode-container');
            container.innerHTML = ''; 

            qrCodeObj = new QRCode(container, {
                text: fullLink,
                width: 180,
                height: 180,
                colorDark: "#000000",
                colorLight: "#ffffff",
                correctLevel: QRCode.CorrectLevel.H
            });

            document.getElementById('qr-modal').classList.remove('hidden');
        }

        function closeQRCodeModal() {
            document.getElementById('qr-modal').classList.add('hidden');
        }

        function copyRoomLink() {
            const fullLink = getDirectRoomURL();
            navigator.clipboard.writeText(fullLink);
            alert("Pautan Bilik telah disalin:\n" + fullLink);
        }

        function backToLobby() {
            if(peer) peer.destroy();
            Object.values(activeCalls).forEach(call => call.close());
            activeCalls = {};
            dataConns = {};
            connectedPeersSet.clear();

            document.getElementById('main-ui').classList.add('hidden');
            document.getElementById('lobby').classList.remove('hidden');

            const grid = document.getElementById('video-grid');
            Array.from(grid.children).forEach(child => {
                if(child.id !== 'local-card') child.remove();
            });
            adjustGrid();
        }
    </script>
</body>
</html>
"""

components.html(meet_html_code, height=800, scrolling=False)