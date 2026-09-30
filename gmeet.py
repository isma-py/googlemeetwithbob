import streamlit as st
import streamlit.components.v1 as components

# Tetapkan konfigurasi skrin penuh
st.set_page_config(
    page_title="Google Meet Clone",
    page_icon="📹",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hilangkan padding laluan Streamlit supaya app kelihatan mesra pengguna
st.markdown("""
    <style>
        .block-container {
            padding-top: 0rem;
            padding-bottom: 0rem;
            padding-left: 0rem;
            padding-right: 0rem;
        }
        header {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Kod Aplikasi Web (HTML/CSS/JS with PeerJS)
meet_html_code = """
<!DOCTYPE html>
<html lang="ms">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Google Meet Clone</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background-color: #202124; color: white; font-family: 'Google Sans', Roboto, Arial, sans-serif; height: 100vh; overflow: hidden; }
        .video-grid { display: grid; gap: 1rem; height: calc(100vh - 90px); padding: 1rem; }
        .video-card { position: relative; background-color: #3c4043; border-radius: 0.5rem; overflow: hidden; display: flex; align-items: center; justify-content: center; }
        video { width: 100%; height: 100%; object-fit: cover; transform: scaleX(-1); }
        .avatar { width: 96px; height: 96px; border-radius: 50%; background-color: #1a73e8; display: flex; align-items: center; justify-content: center; font-size: 2.5rem; font-weight: bold; }
    </style>
</head>
<body class="flex flex-col justify-between">

    <!-- Pre-join Screen / Lobby -->
    <div id="lobby" class="fixed inset-0 z-50 bg-[#202124] flex items-center justify-center p-4">
        <div class="max-w-4xl w-full grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
            <div class="flex flex-col items-center">
                <div class="relative w-full aspect-video bg-[#3c4043] rounded-2xl overflow-hidden flex items-center justify-center border border-gray-700 shadow-xl">
                    <video id="preview-video" autoplay playsinline muted class="w-full h-full object-cover"></video>
                    <div id="preview-avatar" class="avatar hidden">Anda</div>
                    <div class="absolute bottom-4 flex gap-4">
                        <button onclick="togglePreviewMic()" id="btn-prev-mic" class="p-3 rounded-full bg-gray-700 hover:bg-gray-600 text-white transition">
                            <i class="fas fa-microphone" id="icon-prev-mic"></i>
                        </button>
                        <button onclick="togglePreviewCam()" id="btn-prev-cam" class="p-3 rounded-full bg-gray-700 hover:bg-gray-600 text-white transition">
                            <i class="fas fa-video" id="icon-prev-cam"></i>
                        </button>
                    </div>
                </div>
            </div>

            <div class="space-y-6">
                <div>
                    <h1 class="text-3xl font-normal text-white">Sertai Mesyuarat</h1>
                    <p class="text-gray-400 text-sm mt-1">Sambungan Peer-to-Peer WebRTC (STUN Global)</p>
                </div>
                <div class="space-y-4">
                    <input type="text" id="username" placeholder="Nama Anda" class="w-full px-4 py-3 bg-[#202124] border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 text-white" />
                    <div class="flex gap-2">
                        <input type="text" id="room-id-input" placeholder="Kod ID Bilik (Contoh: room123)" class="flex-1 px-4 py-3 bg-[#202124] border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 text-white" />
                        <button onclick="joinRoom()" class="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition">Sertai</button>
                    </div>
                    <div class="relative flex py-2 items-center">
                        <div class="flex-grow border-t border-gray-700"></div>
                        <span class="flex-shrink mx-4 text-gray-500 text-xs uppercase">atau</span>
                        <div class="flex-grow border-t border-gray-700"></div>
                    </div>
                    <button onclick="createRoom()" class="w-full py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-medium rounded-lg transition">
                        <i class="fas fa-plus mr-2"></i>Buka Bilik Baru
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- Main Call UI -->
    <div id="main-ui" class="hidden flex-1 flex relative">
        <div class="flex-1 flex flex-col">
            <!-- Video Grid -->
            <div id="video-grid" class="video-grid grid-cols-1 md:grid-cols-2">
                <!-- Local Video Card -->
                <div class="video-card" id="local-card">
                    <video id="local-video" autoplay playsinline muted></video>
                    <div id="local-avatar" class="avatar hidden">A</div>
                    <div class="absolute bottom-3 left-3 bg-black/50 backdrop-blur px-3 py-1 rounded-md text-xs flex items-center gap-2">
                        <span id="local-name-tag">Anda</span>
                    </div>
                </div>
            </div>

            <!-- Bottom Control Bar -->
            <div class="h-20 bg-[#202124] border-t border-gray-800 px-6 flex items-center justify-between">
                <div class="flex items-center gap-2 text-gray-300">
                    <span id="display-room-id" class="font-mono text-sm bg-gray-800 px-3 py-1.5 rounded-lg border border-gray-700"></span>
                    <button onclick="copyRoomLink()" class="p-2 hover:bg-gray-800 rounded-lg text-gray-400 hover:text-white transition" title="Salin ID Bilik">
                        <i class="far fa-copy"></i>
                    </button>
                </div>

                <div class="flex items-center gap-3">
                    <button onclick="toggleMic()" id="btn-mic" class="p-3.5 rounded-full bg-gray-700 hover:bg-gray-600 text-white transition">
                        <i class="fas fa-microphone" id="icon-mic"></i>
                    </button>
                    <button onclick="toggleCam()" id="btn-cam" class="p-3.5 rounded-full bg-gray-700 hover:bg-gray-600 text-white transition">
                        <i class="fas fa-video" id="icon-cam"></i>
                    </button>
                    <button onclick="toggleScreenShare()" id="btn-screen" class="p-3.5 rounded-full bg-gray-700 hover:bg-gray-600 text-white transition">
                        <i class="fas fa-desktop"></i>
                    </button>
                    <button onclick="leaveCall()" class="p-3.5 rounded-full bg-red-600 hover:bg-red-700 text-white px-6 transition">
                        <i class="fas fa-phone-slash"></i>
                    </button>
                </div>

                <div class="flex items-center gap-2">
                    <button onclick="toggleSidebar('chat')" class="p-3 rounded-full hover:bg-gray-800 text-gray-300 transition relative">
                        <i class="far fa-[#3c4043] fa-comment-alt"></i>
                    </button>
                </div>
            </div>
        </div>

        <!-- Sidebar Chat -->
        <div id="sidebar-chat" class="hidden w-80 bg-[#171717] border-l border-gray-800 flex flex-col h-[calc(100vh-80px)]">
            <div class="p-4 border-b border-gray-800 flex justify-between items-center">
                <h2 class="font-medium">Mesej Dalam Panggilan</h2>
                <button onclick="toggleSidebar('chat')" class="text-gray-400 hover:text-white"><i class="fas fa-times"></i></button>
            </div>
            <div id="chat-messages" class="flex-1 p-4 overflow-y-auto space-y-3 text-sm"></div>
            <div class="p-4 border-t border-gray-800 flex gap-2">
                <input type="text" id="chat-input" placeholder="Hantar mesej..." class="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500" onkeypress="if(event.key==='Enter') sendChatMessage()">
                <button onclick="sendChatMessage()" class="p-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white"><i class="fas fa-paper-plane"></i></button>
            </div>
        </div>
    </div>

    <script>
        let localStream;
        let peer;
        let currentRoomId;
        let myName = "Pengguna";
        let isMicOn = true;
        let isCamOn = true;
        let peers = {};
        let dataConns = {};

        const iceServers = {
            iceServers: [
                { urls: 'stun:stun.l.google.com:19302' },
                { urls: 'stun:stun1.l.google.com:19302' },
                { urls: 'stun:stun2.l.google.com:19302' }
            ]
        };

        async function initPreview() {
            try {
                localStream = await navigator.mediaDevices.getUserMedia({
                    video: { width: { ideal: 1280 }, height: { ideal: 720 } },
                    audio: { echoCancellation: true, noiseSuppression: true }
                });
                document.getElementById('preview-video').srcObject = localStream;
            } catch (err) {
                console.error("Gagal mendapat akses kamera/mikrofon:", err);
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
            const randomId = 'meet-' + Math.random().toString(36).substring(2, 8);
            document.getElementById('room-id-input').value = randomId;
            joinRoom();
        }

        function joinRoom() {
            const nameInput = document.getElementById('username').value.trim();
            const roomInput = document.getElementById('room-id-input').value.trim();
            
            if(!roomInput) { alert("Sila masukkan ID Bilik."); return; }
            if(nameInput) myName = nameInput;

            currentRoomId = roomInput;
            document.getElementById('local-name-tag').innerText = myName;
            document.getElementById('local-avatar').innerText = myName.charAt(0).toUpperCase();
            document.getElementById('display-room-id').innerText = currentRoomId;

            document.getElementById('lobby').classList.add('hidden');
            document.getElementById('main-ui').classList.remove('hidden');

            document.getElementById('local-video').srcObject = localStream;

            // Inisialisasi PeerJS dengan Server WebRTC Public
            peer = new Peer(undefined, { config: iceServers });

            peer.on('open', id => {
                console.log('ID Peer Saya:', id);
                connectToExistingPeers();
            });

            peer.on('call', call => {
                call.answer(localStream);
                const remoteVideo = document.createElement('video');
                remoteVideo.autoplay = true;
                remoteVideo.playsInline = true;

                call.on('stream', remoteStream => {
                    addRemoteStream(call.peer, remoteStream);
                });
            });

            peer.on('connection', conn => {
                setupDataConnection(conn);
            });
        }

        function connectToExistingPeers() {
            // Sambungan automatik berasaskan ID Bilik
            const conn = peer.connect(currentRoomId);
            if(conn) {
                setupDataConnection(conn);
            }
            const call = peer.call(currentRoomId, localStream);
            if(call) {
                call.on('stream', remoteStream => {
                    addRemoteStream(currentRoomId, remoteStream);
                });
            }
        }

        function setupDataConnection(conn) {
            dataConns[conn.peer] = conn;
            conn.on('data', data => {
                if(data.type === 'chat') {
                    appendChatMessage(data.sender, data.message);
                }
            });
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
            tag.className = 'absolute bottom-3 left-3 bg-black/50 backdrop-blur px-3 py-1 rounded-md text-xs';
            tag.innerText = `Ahli (${peerId.substring(0, 5)})`;

            card.appendChild(video);
            card.appendChild(tag);
            grid.appendChild(card);
        }

        function toggleMic() { togglePreviewMic(); }
        function toggleCam() { togglePreviewCam(); }

        async function toggleScreenShare() {
            try {
                const screenStream = await navigator.mediaDevices.getDisplayMedia({ video: true });
                const videoTrack = screenStream.getVideoTracks()[0];
                
                document.getElementById('local-video').srcObject = screenStream;

                videoTrack.onended = () => {
                    document.getElementById('local-video').srcObject = localStream;
                };
            } catch(err) {
                console.error("Pekongsian skrin dibatalkan:", err);
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
            div.className = 'bg-gray-800 p-2.5 rounded-lg';
            div.innerHTML = `<span class="font-semibold text-xs text-blue-400 block">${sender}</span><span class="text-gray-200">${msg}</span>`;
            container.appendChild(div);
            container.scrollTop = container.scrollHeight;
        }

        function copyRoomLink() {
            navigator.clipboard.writeText(currentRoomId);
            alert("ID Bilik telah disalin: " + currentRoomId);
        }

        function leaveCall() {
            location.reload();
        }
    </script>
</body>
</html>
"""

# Paparkan aplikasi HTML/JS terus dalam Streamlit
components.html(meet_html_code, height=850, scrolling=False)