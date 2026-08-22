/**
 * pages/community/Community.jsx
 * Screen 10 - Community Page.
 * Feed from GET /api/community/posts, "Share your experience" composer
 * (POST /api/community/posts), and like/comment-count interactions
 * (POST /api/community/posts/<id>/like).
 */
import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { Heart, MessageCircle, Send, UserCircle, Users } from "lucide-react";
import api from "../../configs/api";
import { useSelector } from "react-redux";
import { useBreadcrumb } from "../../lib/useBreadcrumb";
import { getErrorMessage, formatDate } from "../../lib/formatters";
import SearchToolbar from "../../components/SearchToolbar";
import EmptyState from "../../components/EmptyState";
import Loader from "../../components/Loader";

export default function Community() {
  useBreadcrumb([{ label: "Community" }]);
  const currentUser = useSelector((state) => state.auth.user);

  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState("recent");
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newPost, setNewPost] = useState("");
  const [posting, setPosting] = useState(false);

  const loadPosts = () => {
    setLoading(true);
    api
      .get("/api/community/posts", { params: { search: search || undefined, sort_by: sortBy } })
      .then(({ data }) => setPosts(data.data))
      .catch((err) => toast.error(getErrorMessage(err, "Could not load the community feed.")))
      .finally(() => setLoading(false));
  };

  useEffect(loadPosts, [search, sortBy]);

  const handleShare = async (e) => {
    e.preventDefault();
    if (!newPost.trim()) return;
    setPosting(true);
    try {
      await api.post("/api/community/posts", { content: newPost.trim() });
      setNewPost("");
      toast.success("Shared with the community!");
      loadPosts();
    } catch (err) {
      toast.error(getErrorMessage(err, "Could not share your post."));
    } finally {
      setPosting(false);
    }
  };

  const handleLike = async (postId) => {
    try {
      await api.post(`/api/community/posts/${postId}/like`);
      loadPosts();
    } catch (err) {
      toast.error(getErrorMessage(err, "Could not update like."));
    }
  };

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <div>
        <h1 className="text-xl font-bold text-slate-800 dark:text-slate-100">Community</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400">Trip stories, tips, and recommendations from fellow travelers.</p>
      </div>

      {/* Composer */}
      <form onSubmit={handleShare} className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4 flex items-start gap-3">
        {currentUser?.profile_photo_url ? (
          <img src={currentUser.profile_photo_url} alt="" className="h-9 w-9 rounded-full object-cover shrink-0" />
        ) : (
          <UserCircle size={36} className="text-slate-300 shrink-0" />
        )}
        <div className="flex-1 flex items-center gap-2">
          <input
            value={newPost}
            onChange={(e) => setNewPost(e.target.value)}
            placeholder="Share a travel experience or recommendation..."
            className="flex-1 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-sky-500"
          />
          <button type="submit" disabled={posting || !newPost.trim()} className="inline-flex items-center gap-1.5 rounded-lg bg-sky-600 hover:bg-sky-700 text-white text-sm font-medium px-3 py-2 disabled:opacity-50">
            <Send size={14} /> Share
          </button>
        </div>
      </form>

      <SearchToolbar
        search={search}
        onSearchChange={setSearch}
        searchPlaceholder="Search posts by city, activity, or topic..."
        sortOptions={[
          { value: "recent", label: "Most Recent" },
          { value: "popular", label: "Most Liked" },
        ]}
        sortBy={sortBy}
        onSortByChange={setSortBy}
      />

      {loading ? (
        <Loader label="Loading the feed..." />
      ) : posts.length === 0 ? (
        <EmptyState icon={Users} title="No posts yet" description="Be the first to share a travel story." />
      ) : (
        <div className="space-y-4">
          {posts.map((post) => (
            <article key={post.id} className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4">
              <div className="flex items-center gap-3 mb-2">
                {post.user?.profile_photo_url ? (
                  <img src={post.user.profile_photo_url} alt="" className="h-9 w-9 rounded-full object-cover" />
                ) : (
                  <UserCircle size={36} className="text-slate-300" />
                )}
                <div>
                  <p className="text-sm font-semibold text-slate-800 dark:text-slate-100">{post.user?.full_name || "GlobeTrotter user"}</p>
                  <p className="text-xs text-slate-400">{formatDate(post.created_at)}</p>
                </div>
                {post.category && (
                  <span className="ml-auto text-xs rounded-full bg-sky-50 dark:bg-sky-900/40 text-sky-700 dark:text-sky-300 px-2 py-0.5">
                    {post.category}
                  </span>
                )}
              </div>
              <p className="text-sm text-slate-700 dark:text-slate-200 whitespace-pre-wrap">{post.content}</p>
              {post.image_url && <img src={post.image_url} alt="" className="mt-3 rounded-lg max-h-72 w-full object-cover" />}
              <div className="flex items-center gap-4 mt-3 text-xs text-slate-500 dark:text-slate-400">
                <button onClick={() => handleLike(post.id)} className="flex items-center gap-1.5 hover:text-rose-500">
                  <Heart size={14} /> {post.like_count}
                </button>
                <span className="flex items-center gap-1.5">
                  <MessageCircle size={14} /> {post.comment_count}
                </span>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
