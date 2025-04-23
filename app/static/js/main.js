// WenShu - 主JavaScript文件

// Vue应用实例
new Vue({
    el: '#app',
    data: {
        // 连接相关
        connectionModalVisible: false,
        connecting: false,
        connectionForm: {
            db_type: 'mysql',
            host: 'localhost',
            port: '3306',
            database: '',
            user: 'root',
            password: ''
        },
        currentConnection: null,
        
        // 对话相关
        conversations: [],
        currentConversationIndex: -1,
        userInput: '',
        loading: false,
        
        // SQL输入
        sqlModalVisible: false,
        sqlInput: '',
        sqlLoading: false,
        
        // 元数据显示
        metadataModalVisible: false
    },
    
    computed: {
        // 当前对话的消息列表
        currentMessages() {
            if (this.currentConversationIndex < 0 || !this.conversations.length) {
                return [];
            }
            return this.conversations[this.currentConversationIndex].messages;
        }
    },
    
    created() {
        // 初始化创建一个新会话
        this.createNewConversation();
    },
    
    methods: {
        // 显示连接数据库对话框
        showConnectionModal() {
            this.connectionModalVisible = true;
        },
        
        // 连接数据库
        connectDatabase() {
            this.connecting = true;
            
            // 发送连接请求
            axios.post('/api/connect', this.connectionForm)
                .then(response => {
                    this.connecting = false;
                    
                    if (response.data.status === 'success') {
                        // 保存连接信息
                        this.currentConnection = response.data;
                        
                        // 创建新会话
                        this.createNewConversation();
                        
                        // 关闭对话框
                        this.connectionModalVisible = false;
                        
                        // 显示成功消息
                        this.$message.success('数据库连接成功');
                    } else {
                        this.$message.error(response.data.message || '连接失败');
                    }
                })
                .catch(error => {
                    this.connecting = false;
                    this.$message.error('连接请求失败: ' + (error.response?.data?.message || error.message));
                });
        },
        
        // 断开数据库连接
        disconnectDatabase() {
            if (!this.currentConnection) return;
            
            axios.post('/api/disconnect', {
                connection_id: this.currentConnection.connection_id
            })
                .then(response => {
                    if (response.data.status === 'success' || response.data.status === 'warning') {
                        this.currentConnection = null;
                        this.$message.success('已断开数据库连接');
                    } else {
                        this.$message.error(response.data.message || '断开连接失败');
                    }
                })
                .catch(error => {
                    this.$message.error('断开连接请求失败: ' + (error.response?.data?.message || error.message));
                });
        },
        
        // 处理下拉菜单命令
        handleCommand(command) {
            if (command === 'disconnect') {
                this.disconnectDatabase();
            } else if (command === 'viewMetadata') {
                this.metadataModalVisible = true;
            }
        },
        
        // 创建新会话
        createNewConversation() {
            const newConversation = {
                title: '未命名会话 ' + (this.conversations.length + 1),
                timestamp: new Date().toISOString(),
                messages: []
            };
            
            this.conversations.push(newConversation);
            this.currentConversationIndex = this.conversations.length - 1;
        },
        
        // 选择会话
        selectConversation(index) {
            this.currentConversationIndex = index;
            
            // 滚动到底部
            this.$nextTick(() => {
                this.scrollToBottom();
            });
        },
        
        // 发送查询
        sendQuery() {
            if (!this.userInput.trim() || !this.currentConnection) return;
            
            // 添加用户消息
            this.addMessage('user', this.userInput);
            
            // 记录用户输入并清空输入框
            const query = this.userInput;
            this.userInput = '';
            
            // 显示加载状态
            this.loading = true;
            
            // 构建对话历史
            const history = this.conversations[this.currentConversationIndex].messages
                .slice(0, -1) // 不包括刚刚添加的用户消息
                .map(msg => ({
                    role: msg.role,
                    content: msg.content
                }));
            
            // 发送查询请求
            axios.post('/api/query', {
                connection_id: this.currentConnection.connection_id,
                query: query,
                conversation_history: history
            })
                .then(response => {
                    this.loading = false;
                    
                    if (response.data.status === 'success') {
                        // 添加助手回复
                        const assistantMessage = {
                            role: 'assistant',
                            content: response.data.result_explanation || response.data.explanation,
                            sql: response.data.sql,
                            results: response.data.results,
                            timestamp: new Date().toISOString()
                        };
                        
                        // 如果是修正的SQL，添加更多信息
                        if (response.data.revised) {
                            assistantMessage.original_sql = response.data.original_sql;
                            assistantMessage.original_explanation = response.data.original_explanation;
                        }
                        
                        this.addMessage('assistant', assistantMessage.content, assistantMessage);
                        
                        // 如果有查询结果，更新会话标题
                        if (this.conversations[this.currentConversationIndex].title.startsWith('未命名会话')) {
                            this.conversations[this.currentConversationIndex].title = this.truncateText(query, 30);
                        }
                    } else {
                        // 添加错误回复
                        this.addMessage('assistant', `查询失败: ${response.data.message}`);
                    }
                })
                .catch(error => {
                    this.loading = false;
                    this.addMessage('assistant', `查询请求失败: ${error.message}`);
                });
        },
        
        // 显示SQL输入对话框
        showSqlInput() {
            if (!this.currentConnection) {
                this.$message.warning('请先连接数据库');
                return;
            }
            
            this.sqlInput = '';
            this.sqlModalVisible = true;
        },
        
        // 执行SQL
        executeSql() {
            if (!this.sqlInput.trim() || !this.currentConnection) return;
            
            this.sqlLoading = true;
            
            // 发送执行SQL请求
            axios.post('/api/execute', {
                connection_id: this.currentConnection.connection_id,
                sql: this.sqlInput
            })
                .then(response => {
                    this.sqlLoading = false;
                    
                    if (response.data.status === 'success') {
                        // 添加用户消息
                        this.addMessage('user', `SQL: ${this.sqlInput}`);
                        
                        // 关闭对话框
                        this.sqlModalVisible = false;
                        
                        // 添加助手回复
                        const assistantMessage = {
                            role: 'assistant',
                            content: '执行SQL查询成功',
                            sql: response.data.sql,
                            results: response.data.results,
                            timestamp: new Date().toISOString()
                        };
                        
                        this.addMessage('assistant', assistantMessage.content, assistantMessage);
                    } else {
                        this.$message.error(response.data.message || 'SQL执行失败');
                    }
                })
                .catch(error => {
                    this.sqlLoading = false;
                    this.$message.error('执行SQL请求失败: ' + (error.response?.data?.message || error.message));
                });
        },
        
        // 添加消息到当前会话
        addMessage(role, content, extraData = {}) {
            if (this.currentConversationIndex < 0) {
                this.createNewConversation();
            }
            
            const message = {
                role: role,
                content: content,
                timestamp: new Date().toISOString(),
                ...extraData
            };
            
            this.conversations[this.currentConversationIndex].messages.push(message);
            
            // 滚动到底部
            this.$nextTick(() => {
                this.scrollToBottom();
            });
            
            return message;
        },
        
        // 复制SQL
        copySql(sql) {
            navigator.clipboard.writeText(sql)
                .then(() => {
                    this.$message.success('SQL已复制到剪贴板');
                })
                .catch(() => {
                    this.$message.error('复制失败，请手动复制');
                    
                    // 创建临时文本区域
                    const textarea = document.createElement('textarea');
                    textarea.value = sql;
                    document.body.appendChild(textarea);
                    textarea.select();
                    document.execCommand('copy');
                    document.body.removeChild(textarea);
                    
                    this.$message.success('SQL已复制到剪贴板');
                });
        },
        
        // 导出查询结果
        exportResults(results) {
            if (!results || !results.rows || !results.rows.length) {
                this.$message.warning('没有数据可导出');
                return;
            }
            
            try {
                // 转换为CSV格式
                const columns = results.columns;
                let csv = columns.join(',') + '\n';
                
                for (const row of results.rows) {
                    const values = columns.map(col => {
                        let value = row[col];
                        if (value === null || value === undefined) return '';
                        value = String(value);
                        // 如果包含逗号、引号或换行符，用引号包裹
                        if (value.includes(',') || value.includes('"') || value.includes('\n')) {
                            return '"' + value.replace(/"/g, '""') + '"';
                        }
                        return value;
                    });
                    csv += values.join(',') + '\n';
                }
                
                // 创建下载链接
                const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
                const url = URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                link.setAttribute('download', 'query_results.csv');
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                
                this.$message.success('查询结果已导出为CSV文件');
            } catch (error) {
                this.$message.error('导出失败: ' + error.message);
            }
        },
        
        // 滚动聊天区域到底部
        scrollToBottom() {
            const chatMessages = this.$refs.chatMessages;
            if (chatMessages) {
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        },
        
        // 文本截断，用于会话标题
        truncateText(text, maxLength) {
            if (text.length <= maxLength) return text;
            return text.substring(0, maxLength) + '...';
        },
        
        // 格式化消息内容（支持Markdown）
        formatMessage(content) {
            if (!content) return '';
            
            try {
                // 使用marked库解析Markdown
                return marked.parse(content);
            } catch (error) {
                console.error('Markdown解析错误', error);
                return content;
            }
        }
    }
}); 