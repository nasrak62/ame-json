
const userProfile = document.getElementById('user-profile');

const assembler = new ProgressiveAssembler();

fetch('/stream')
    .then(response => {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        function read() {
            reader.read().then(({ done, value }) => {
                if (done) {
                    console.log('Stream complete');
                    return;
                }

                const chunk = decoder.decode(value, { stream: true });
                const parts = chunk.split('\n');

                parts.forEach(part => {
                    if (part) {
                        try {
                            const { is_finished, data } = assembler.assemble(part);
                            userProfile.textContent = JSON.stringify(data, null, 2);
                            if (is_finished) {
                                console.log('Stream finished');
                                reader.cancel();
                            }
                        } catch (e) {
                            console.error('Error parsing JSON:', e, 'on part:', part);
                        }
                    }
                });

                read();
            });
        }

        read();
    })
    .catch(error => {
        console.error('Fetch error:', error);
    });

