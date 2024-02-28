
async function subscribe_toggle(action) {
    try {
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const url = `subscribe_toggle/${action}/`;
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
        });

        if (!response.ok) {
            console.error('Network response was not ok');
            return;
        }

        const data = await response.json();
        updateButton(data);
        updateSubscribersCount(data.subscribers_count);
    } catch (error) {
        console.error('Error:', error.message);
    }
}

function updateButton(data) {
    const button = document.getElementById('subscribeButton');
    button.innerText = data.is_subscribed ? 'Subscribe' : 'Unsubscribe';
    button.onclick = () => subscribe_toggle(data.is_subscribed ? 'subscribe' : 'unsubscribe');
}

function updateSubscribersCount(count) {
    const subscribersCountElement = document.getElementById('subscribersCount');
    if (subscribersCountElement) {
        subscribersCountElement.innerText = `${count} subscribers`;
    }
}

document.querySelectorAll('.like-button, .dislike-button').forEach(button => {
    button.addEventListener('click', async function() {
        const postId = this.getAttribute('data-post-id');
        const action = this.getAttribute('data-action');
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const toggleLikeUrl = `/user/toggle_like/${postId}/${action}/`;

        try {
            const response = await fetch(toggleLikeUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                },
            });

        if (!response.ok) {
            console.error('Network response was not ok');
            return;
        }

            const data = await response.json();
            updateLikesAndDislikes(data);
        } catch (error) {
            console.error('Error:', error.message);
        }
    });
});

function updateLikesAndDislikes(data) {
    document.getElementById(`like-count-${data.post_id}`).innerText = data.likes;
    document.getElementById(`dislike-count-${data.post_id}`).innerText = data.dislikes;
}