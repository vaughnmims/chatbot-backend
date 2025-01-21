@app.route("/generate", methods=["POST"])
def generate_text():
    try:
        # Get data from the request
        data = request.json
        prompt = data.get("prompt", "")
        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400

        # Call OpenAI API
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=100
        )

        # Return the OpenAI response
        return jsonify({"response": response.choices[0].text.strip()}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
