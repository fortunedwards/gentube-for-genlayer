// Vue.js Application
const { createApp } = Vue;

createApp({
    data() {
        return {
            currentView: 'home', // 'home' or 'archive'
            videos: [],
            filteredVideos: [],
            displayedVideos: [],
            searchQuery: '',
            selectedSpeaker: '',
            selectedPlatform: '',
            selectedTag: '',
            speakers: [],
            platforms: [],
            tags: [],

            loading: true,

            isDarkMode: false,
            isOnline: navigator.onLine,
            showInstallPrompt: false,

            deferredPrompt: null,
            itemsPerPage: 12,
            currentPage: 1,
            isLoadingMore: false,
            showVideoPlayer: false,
            currentVideo: null
        }
    },
    
    async mounted() {
        // Initialize theme
        this.initializeTheme();
        
        // Load videos
        await this.loadVideos();
        
        // Setup infinite scroll
        this.setupInfiniteScroll();
        
        // Setup PWA
        this.setupPWA();
        
        // Setup online/offline detection
        this.setupNetworkDetection();
        
        // Setup keyboard shortcuts
        this.setupKeyboardShortcuts();
    },
    
    methods: {
        async loadVideos() {
            try {
                this.loading = true;
                
                // Try to load from cache first (offline support)
                const cachedVideos = this.getCachedVideos();
                if (cachedVideos && !this.isOnline) {
                    this.videos = cachedVideos;
                    this.processVideos();
                    this.loading = false;
                    return;
                }
                
                // Load from server
                const response = await fetch('videos.json');
                if (!response.ok) throw new Error('Failed to load videos');
                
                const data = await response.json();
                this.videos = this.processVideoData(data);
                
                // Cache for offline use
                this.cacheVideos(this.videos);
                
                this.processVideos();
                
            } catch (error) {
                console.error('Error loading videos:', error);
                
                // Try to load from cache as fallback
                const cachedVideos = this.getCachedVideos();
                if (cachedVideos) {
                    this.videos = cachedVideos;
                    this.processVideos();
                } else {
                    this.videos = [];
                }
            } finally {
                this.loading = false;
            }
        },
        
        processVideoData(data) {
            return data.map(video => ({
                ...video,
                thumbnail: this.extractThumbnail(video),
                platform: this.detectPlatform(video.url),
                duration: this.extractDuration(video)
            }));
        },
        
        extractThumbnail(video) {
            // Try to get thumbnail from metadata first
            if (video.metadata && video.metadata.thumbnail) {
                return video.metadata.thumbnail;
            }
            
            // Generate thumbnail from URL for known platforms
            if (video.url.includes('youtube.com') || video.url.includes('youtu.be')) {
                const videoId = this.extractYouTubeId(video.url);
                return videoId ? `https://img.youtube.com/vi/${videoId}/hqdefault.jpg` : null;
            }
            
            if (video.url.includes('vimeo.com')) {
                // Vimeo thumbnails require API call, skip for now
                return null;
            }
            
            return null;
        },
        
        extractYouTubeId(url) {
            const regex = /(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)/;
            const match = url.match(regex);
            return match ? match[1] : null;
        },
        
        detectPlatform(url) {
            if (url.includes('youtube.com') || url.includes('youtu.be')) return 'YouTube';
            if (url.includes('vimeo.com')) return 'Vimeo';
            if (url.includes('twitter.com') || url.includes('x.com')) return 'Twitter';
            if (url.includes('linkedin.com')) return 'LinkedIn';
            if (url.includes('facebook.com')) return 'Facebook';
            if (url.includes('tiktok.com')) return 'TikTok';
            return 'Other';
        },
        
        extractDuration(video) {
            if (video.metadata && video.metadata.duration) {
                return video.metadata.duration;
            }
            return null;
        },
        
        processVideos() {
            // Extract unique speakers, platforms, and tags
            const allSpeakers = this.videos.flatMap(v => {
                if (Array.isArray(v.speakers)) return v.speakers;
                if (v.speaker) return [v.speaker];
                return [];
            });
            this.speakers = [...new Set(allSpeakers)].sort();
            this.platforms = [...new Set(this.videos.map(v => v.platform))].filter(Boolean).sort();
            this.tags = [...new Set(this.videos.flatMap(v => v.tags || []))].filter(Boolean).sort();
            
            // Apply filters
            this.applyFilters();
        },
        
        applyFilters() {
            let filtered = this.videos;
            
            // Search filter
            if (this.searchQuery) {
                const query = this.searchQuery.toLowerCase();
                filtered = filtered.filter(video => {
                    const speakerMatch = Array.isArray(video.speakers) 
                        ? video.speakers.some(s => s.toLowerCase().includes(query))
                        : video.speaker?.toLowerCase().includes(query);
                    
                    return video.title.toLowerCase().includes(query) ||
                        video.description.toLowerCase().includes(query) ||
                        speakerMatch ||
                        (video.tags && video.tags.some(tag => tag.toLowerCase().includes(query)));
                });
            }
            
            // Speaker filter
            if (this.selectedSpeaker) {
                filtered = filtered.filter(video => {
                    if (Array.isArray(video.speakers)) {
                        return video.speakers.includes(this.selectedSpeaker);
                    }
                    return video.speaker === this.selectedSpeaker;
                });
            }
            
            // Platform filter
            if (this.selectedPlatform) {
                filtered = filtered.filter(video => video.platform === this.selectedPlatform);
            }
            
            // Tag filter
            if (this.selectedTag) {
                filtered = filtered.filter(video => video.tags && video.tags.includes(this.selectedTag));
            }
            
            this.filteredVideos = filtered;
            this.currentPage = 1;
            this.updateDisplayedVideos();
        },
        
        updateDisplayedVideos() {
            const startIndex = 0;
            const endIndex = this.currentPage * this.itemsPerPage;
            this.displayedVideos = this.filteredVideos.slice(startIndex, endIndex);
        },
        
        loadMoreVideos() {
            if (this.isLoadingMore) return;
            
            const totalPages = Math.ceil(this.filteredVideos.length / this.itemsPerPage);
            if (this.currentPage >= totalPages) return;
            
            this.isLoadingMore = true;
            this.currentPage++;
            
            // Simulate loading delay for better UX
            setTimeout(() => {
                const startIndex = (this.currentPage - 1) * this.itemsPerPage;
                const endIndex = this.currentPage * this.itemsPerPage;
                const newVideos = this.filteredVideos.slice(startIndex, endIndex);
                
                // Add animation class to new items
                newVideos.forEach(video => video.isNew = true);
                
                this.displayedVideos.push(...newVideos);
                this.isLoadingMore = false;
                
                // Remove animation class after animation completes
                setTimeout(() => {
                    newVideos.forEach(video => video.isNew = false);
                }, 500);
            }, 300);
        },
        
        setupInfiniteScroll() {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting && !this.loading && !this.isLoadingMore) {
                        this.loadMoreVideos();
                    }
                });
            }, {
                rootMargin: '100px'
            });
            
            // Create a sentinel element
            const sentinel = document.createElement('div');
            sentinel.style.height = '1px';
            sentinel.className = 'scroll-sentinel';
            
            this.$nextTick(() => {
                const videoGrid = this.$refs.videoGrid;
                if (videoGrid) {
                    videoGrid.appendChild(sentinel);
                    observer.observe(sentinel);
                }
            });
        },
        
        handleSearch() {
            clearTimeout(this.searchTimeout);
            this.searchTimeout = setTimeout(() => {
                this.applyFilters();
            }, 300);
        },
        
        handleFilter() {
            this.applyFilters();
        },
        
        toggleTag(tag) {
            this.selectedTag = this.selectedTag === tag ? '' : tag;
            this.applyFilters();
        },
        
        clearFilters() {
            this.searchQuery = '';
            this.selectedSpeaker = '';
            this.selectedPlatform = '';
            this.selectedTag = '';
            this.applyFilters();
        },
        
        hasActiveFilters() {
            return this.searchQuery || this.selectedSpeaker || this.selectedPlatform || this.selectedTag;
        },
        
        // Theme Management
        initializeTheme() {
            const savedTheme = localStorage.getItem('theme');
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            
            this.isDarkMode = savedTheme === 'dark' || (!savedTheme && prefersDark);
            this.applyTheme();
            
            // Listen for system theme changes
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
                if (!localStorage.getItem('theme')) {
                    this.isDarkMode = e.matches;
                    this.applyTheme();
                }
            });
        },
        
        toggleDarkMode() {
            this.isDarkMode = !this.isDarkMode;
            this.applyTheme();
            localStorage.setItem('theme', this.isDarkMode ? 'dark' : 'light');
        },
        
        applyTheme() {
            if (this.isDarkMode) {
                document.documentElement.classList.add('dark');
            } else {
                document.documentElement.classList.remove('dark');
            }
            document.querySelector('meta[name="theme-color"]').content = this.isDarkMode ? '#101022' : '#1313ec';
        },
        
        // PWA Setup
        setupPWA() {
            // Listen for install prompt
            window.addEventListener('beforeinstallprompt', (e) => {
                e.preventDefault();
                this.deferredPrompt = e;
                this.showInstallPrompt = true;
            });
            
            // Hide install prompt after installation
            window.addEventListener('appinstalled', () => {
                this.showInstallPrompt = false;
                this.deferredPrompt = null;
            });
        },
        
        async installPWA() {
            if (!this.deferredPrompt) return;
            
            this.deferredPrompt.prompt();
            const { outcome } = await this.deferredPrompt.userChoice;
            
            if (outcome === 'accepted') {
                this.showInstallPrompt = false;
            }
            
            this.deferredPrompt = null;
        },
        
        dismissInstall() {
            this.showInstallPrompt = false;
            localStorage.setItem('installPromptDismissed', Date.now());
        },
        
        // Network Detection
        setupNetworkDetection() {
            window.addEventListener('online', () => {
                this.isOnline = true;
                this.loadVideos(); // Refresh data when back online
            });
            
            window.addEventListener('offline', () => {
                this.isOnline = false;
            });
        },
        
        // Caching for Offline Support
        cacheVideos(videos) {
            try {
                localStorage.setItem('cachedVideos', JSON.stringify(videos));
                localStorage.setItem('cacheTimestamp', Date.now());
            } catch (error) {
                console.warn('Failed to cache videos:', error);
            }
        },
        
        getCachedVideos() {
            try {
                const cached = localStorage.getItem('cachedVideos');
                const timestamp = localStorage.getItem('cacheTimestamp');
                
                // Cache expires after 1 hour
                if (cached && timestamp && (Date.now() - timestamp < 3600000)) {
                    return JSON.parse(cached);
                }
            } catch (error) {
                console.warn('Failed to load cached videos:', error);
            }
            return null;
        },
        
        // Keyboard Shortcuts
        setupKeyboardShortcuts() {
            document.addEventListener('keydown', (e) => {
                // Ctrl/Cmd + K to focus search
                if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                    e.preventDefault();
                    document.querySelector('input[placeholder="Search videos..."]')?.focus();
                }
                
                // Escape to close video player
                if (e.key === 'Escape') {
                    if (this.showVideoPlayer) {
                        this.closeVideoPlayer();
                    }
                }
                
                // Ctrl/Cmd + D to toggle dark mode
                if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
                    e.preventDefault();
                    this.toggleDarkMode();
                }
            });
        },
        
        // Utility Methods
        formatDate(dateString) {
            const date = new Date(dateString);
            const now = new Date();
            const diffTime = Math.abs(now - date);
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            
            if (diffDays === 1) return 'Yesterday';
            if (diffDays < 7) return `${diffDays} days ago`;
            if (diffDays < 30) return `${Math.ceil(diffDays / 7)} weeks ago`;
            if (diffDays < 365) return `${Math.ceil(diffDays / 30)} months ago`;
            return `${Math.ceil(diffDays / 365)} years ago`;
        },
        
        formatDuration(seconds) {
            if (!seconds) return '';
            
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            const secs = seconds % 60;
            
            if (hours > 0) {
                return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
            }
            return `${minutes}:${secs.toString().padStart(2, '0')}`;
        },
        
        truncateText(text, maxLength) {
            if (!text || text.length <= maxLength) return text;
            return text.substring(0, maxLength) + '...';
        },
        
        handleImageError(event) {
            event.target.style.display = 'none';
            event.target.parentElement.querySelector('.no-thumbnail').style.display = 'flex';
        },
        
        // Video Player Methods
        watchVideo(video) {
            this.currentVideo = video;
            this.showVideoPlayer = true;
            document.body.style.overflow = 'hidden'; // Prevent background scrolling
        },
        
        closeVideoPlayer() {
            this.showVideoPlayer = false;
            this.currentVideo = null;
            document.body.style.overflow = 'auto';
        },
        
        getEmbedUrl(url) {
            // YouTube
            if (url.includes('youtube.com') || url.includes('youtu.be')) {
                const videoId = this.extractYouTubeId(url);
                return videoId ? `https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0` : null;
            }
            
            // Vimeo
            if (url.includes('vimeo.com')) {
                const videoId = url.split('/').pop().split('?')[0];
                return `https://player.vimeo.com/video/${videoId}?autoplay=1`;
            }
            
            // Dailymotion
            if (url.includes('dailymotion.com')) {
                const videoId = url.split('/video/')[1]?.split('?')[0];
                return videoId ? `https://www.dailymotion.com/embed/video/${videoId}?autoplay=1` : null;
            }
            
            // Twitter/X - Cannot be embedded
            if (url.includes('x.com') || url.includes('twitter.com')) {
                return null;
            }
            
            return null;
        },
        
        canEmbed(url) {
            return this.getEmbedUrl(url) !== null;
        },
        
        // Navigation Methods
        goToHome() {
            this.currentView = 'home';
        },
        
        goToArchive() {
            this.currentView = 'archive';
        },
        
        getFeaturedVideo() {
            const youtubeVideos = this.videos.filter(video => 
                video.url.includes('youtube.com') || video.url.includes('youtu.be')
            );
            if (youtubeVideos.length === 0) return null;
            return youtubeVideos[Math.floor(Math.random() * youtubeVideos.length)];
        },
        
        getRecentVideos() {
            return this.videos.slice(0, 6);
        },
        
        getVideosByTag(tag) {
            return this.videos.filter(video => video.tags && video.tags.includes(tag)).slice(0, 6);
        }
    }
}).mount('#app');