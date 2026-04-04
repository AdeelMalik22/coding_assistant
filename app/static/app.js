/* JavaScript for API Builder */

console.log('API Builder loaded');

// Highlight.js setup (if available)
if (typeof hljs !== 'undefined') {
    document.addEventListener('DOMContentLoaded', () => {
        hljs.highlightAll();
    });
}

// API Helper Functions
class APIBuilder {
    static async generateAPI(prompt, rules = {}) {
        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    prompt,
                    jwt_auth: rules.jwt_auth || false,
                    crud_operations: rules.crud_operations || false,
                    user_model: rules.user_model || false,
                    database: rules.database !== false,
                    custom_rules: rules.custom_rules || [],
                }),
            });

            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Generation error:', error);
            throw error;
        }
    }

    static async getProjectInfo(projectId) {
        try {
            const response = await fetch(`/api/projects/${projectId}`);
            if (!response.ok) {
                throw new Error(`Project not found: ${projectId}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching project:', error);
            throw error;
        }
    }

    static async getFile(projectId, filename) {
        try {
            const response = await fetch(`/api/projects/${projectId}/files/${filename}`);
            if (!response.ok) {
                throw new Error(`File not found: ${filename}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching file:', error);
            throw error;
        }
    }

    static async updateFile(projectId, filename, content) {
        try {
            const response = await fetch(`/api/projects/${projectId}/files/${filename}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ content }),
            });

            if (!response.ok) {
                throw new Error('Failed to update file');
            }

            return await response.json();
        } catch (error) {
            console.error('Error updating file:', error);
            throw error;
        }
    }

    static async regenerateFile(projectId, filename) {
        try {
            const response = await fetch(`/api/projects/${projectId}/regenerate/${filename}`, {
                method: 'POST',
            });

            if (!response.ok) {
                throw new Error('Failed to regenerate file');
            }

            return await response.json();
        } catch (error) {
            console.error('Error regenerating file:', error);
            throw error;
        }
    }
}

// UI Helper Functions
class UIHelper {
    static showLoading(message = 'Loading...') {
        const loader = document.createElement('div');
        loader.id = 'loader';
        loader.className = 'loader';
        loader.innerHTML = `
            <div class="loader-content">
                <div class="loading"></div>
                <p>${message}</p>
            </div>
        `;
        document.body.appendChild(loader);
    }

    static hideLoading() {
        const loader = document.getElementById('loader');
        if (loader) {
            loader.remove();
        }
    }

    static showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            background: ${type === 'error' ? '#dc3545' : type === 'success' ? '#28a745' : '#0066cc'};
            color: white;
            border-radius: 4px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            z-index: 1000;
            animation: slideIn 0.3s ease-in-out;
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-in-out';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    static copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showNotification('Copied to clipboard!', 'success');
        }).catch(() => {
            this.showNotification('Failed to copy', 'error');
        });
    }
}

// Form handling
document.addEventListener('DOMContentLoaded', () => {
    // Prompt form submission
    const promptForm = document.querySelector('.prompt-form');
    if (promptForm) {
        promptForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const submitBtn = promptForm.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.innerHTML = '⏳ Generating...';
        });
    }

    // Copy buttons
    document.querySelectorAll('.copy-btn').forEach((btn) => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const codeBlock = btn.closest('.file-display')?.querySelector('code');
            if (codeBlock) {
                UIHelper.copyToClipboard(codeBlock.textContent);
            }
        });
    });

    // Add styles for animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }

        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(400px);
                opacity: 0;
            }
        }

        .loader {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 999;
        }

        .loader-content {
            text-align: center;
            color: white;
        }

        .loading {
            display: inline-block;
            width: 40px;
            height: 40px;
            border: 4px solid rgba(255, 255, 255, 0.3);
            border-top-color: white;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 20px;
        }

        @keyframes spin {
            to {
                transform: rotate(360deg);
            }
        }
    `;
    document.head.appendChild(style);
});

// Export for use in other scripts
window.APIBuilder = APIBuilder;
window.UIHelper = UIHelper;

