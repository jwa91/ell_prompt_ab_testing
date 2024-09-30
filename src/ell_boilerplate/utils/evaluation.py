import sqlite3
import matplotlib.pyplot as plt
import numpy as np
import os

# Database path
db_path = './logdir/ell.db'
output_dir = './output'

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

def get_all_versions_lmp_ids(name):
    """Get all LMP IDs for a given function name, ordered by version number."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # SQL query to fetch all lmp_ids for the given name, ordered by version
    cursor.execute("""
        SELECT lmp_id, version_number FROM serializedlmp 
        WHERE name = ? 
        ORDER BY version_number DESC, created_at DESC
    """, (name,))
    
    versions = cursor.fetchall()  # Returns a list of tuples (lmp_id, version_number)
    conn.close()
    return versions

def fetch_avg_scores_per_lmp(lmp_id):
    """Fetch average scores for a given LMP ID."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Fetch the average latency for the given LMP
    cursor.execute("SELECT AVG(latency_ms) FROM invocation WHERE lmp_id = ?", (lmp_id,))
    avg_latency = cursor.fetchone()[0]

    # Fetch the average cosine similarity for the given LMP
    cursor.execute("""
        SELECT AVG(e.metric_value)
        FROM evaluation e
        JOIN invocation i ON e.invocation_id = i.id
        WHERE i.lmp_id = ? AND e.metric_name = 'cosine_similarity'
    """, (lmp_id,))
    avg_cosine_similarity = cursor.fetchone()[0]

    # Fetch the average completeness for the given LMP
    cursor.execute("""
        SELECT AVG(e.metric_value)
        FROM evaluation e
        JOIN invocation i ON e.invocation_id = i.id
        WHERE i.lmp_id = ? AND e.metric_name = 'completeness'
    """, (lmp_id,))
    avg_completeness = cursor.fetchone()[0]

    # Fetch the average objectivity for the given LMP
    cursor.execute("""
        SELECT AVG(e.metric_value)
        FROM evaluation e
        JOIN invocation i ON e.invocation_id = i.id
        WHERE i.lmp_id = ? AND e.metric_name = 'objectivity'
    """, (lmp_id,))
    avg_objectivity = cursor.fetchone()[0]

    conn.close()

    # Return all the fetched scores, replacing None with 0.0 for safety
    return (
        avg_latency if avg_latency is not None else 0.0,
        avg_cosine_similarity if avg_cosine_similarity is not None else 0.0,
        avg_completeness if avg_completeness is not None else 0.0,
        avg_objectivity if avg_objectivity is not None else 0.0
    )

def plot_metric(metric_name, versions_v1, versions_v2, scores_v1, scores_v2):
    """Create a bar chart for a specific metric."""
    fig, ax = plt.subplots()

    bar_width = 0.35
    index = np.arange(len(versions_v1) + len(versions_v2))

    # Combine version labels
    version_labels = [f'v1 v{v+1}' for _, v in versions_v1] + [f'v2 v{v+1}' for _, v in versions_v2]

    # Extract the specific metric values (e.g., latency, cosine similarity)
    v1_metric_values = [scores[0 if metric_name == 'Latency' else 1 if metric_name == 'Cosine Similarity'
                            else 2 if metric_name == 'Completeness' else 3] for scores in scores_v1]
    v2_metric_values = [scores[0 if metric_name == 'Latency' else 1 if metric_name == 'Cosine Similarity'
                            else 2 if metric_name == 'Completeness' else 3] for scores in scores_v2]

    # Combine both LMP versions for plotting
    metric_values = v1_metric_values + v2_metric_values

    # Plot bars
    ax.bar(index, metric_values, bar_width, color=['blue'] * len(v1_metric_values) + ['orange'] * len(v2_metric_values))

    # Set labels and title
    ax.set_xlabel('Versions')
    ax.set_ylabel(metric_name)
    ax.set_title(f'Comparison of {metric_name} for summarize_news_v1 vs summarize_news_v2')
    ax.set_xticks(index)
    ax.set_xticklabels(version_labels, rotation=45, ha='right')
    
    # Save the figure
    output_path = f'{metric_name.lower().replace(" ", "_")}_comparison.png'
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, output_path))
    plt.close()
    
    return output_path

def save_to_markdown(scores_v1, scores_v2, versions_v1, versions_v2, file_paths):
    """Generate a markdown file with summary and graphs."""
    markdown_path = os.path.join(output_dir, 'summary_comparison.md')
    with open(markdown_path, 'w') as f:
        # Write summary
        f.write('# Summary Comparison for summarize_news_v1 and summarize_news_v2\n\n')

        f.write('## summarize_news_v1\n')
        for (lmp_id, version), scores in zip(versions_v1, scores_v1):
            f.write(f'### Version {version + 1}\n')
            f.write(f'- Latency: {scores[0]:.2f} ms\n')
            f.write(f'- Cosine Similarity: {scores[1]:.2f}\n')
            f.write(f'- Completeness: {scores[2]:.2f}\n')
            f.write(f'- Objectivity: {scores[3]:.2f}\n\n')

        f.write('## summarize_news_v2\n')
        for (lmp_id, version), scores in zip(versions_v2, scores_v2):
            f.write(f'### Version {version + 1}\n')
            f.write(f'- Latency: {scores[0]:.2f} ms\n')
            f.write(f'- Cosine Similarity: {scores[1]:.2f}\n')
            f.write(f'- Completeness: {scores[2]:.2f}\n')
            f.write(f'- Objectivity: {scores[3]:.2f}\n\n')

        # Add graphs to markdown
        f.write('## Graphical Comparison\n')
        for metric, file_path in file_paths.items():
            f.write(f'### {metric} Comparison\n')
            f.write(f'![{metric}]({file_path})\n\n')

def main():
    # Fetch all versions of summarize_news_v1 and summarize_news_v2
    versions_v1 = get_all_versions_lmp_ids('summarize_news_v1')
    versions_v2 = get_all_versions_lmp_ids('summarize_news_v2')

    # Fetch average scores for each version of summarize_news_v1
    scores_v1 = [fetch_avg_scores_per_lmp(lmp_id) for lmp_id, _ in versions_v1]

    # Fetch average scores for each version of summarize_news_v2
    scores_v2 = [fetch_avg_scores_per_lmp(lmp_id) for lmp_id, _ in versions_v2]

    # Plot each metric separately and save the paths
    metrics = ['Latency', 'Cosine Similarity', 'Completeness', 'Objectivity']
    file_paths = {metric: plot_metric(metric, versions_v1, versions_v2, scores_v1, scores_v2) for metric in metrics}

    # Save the results to a markdown file with the graphs
    save_to_markdown(scores_v1, scores_v2, versions_v1, versions_v2, file_paths)

if __name__ == "__main__":
    main()